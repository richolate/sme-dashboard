"""Background tasks for data processing"""
from celery import shared_task
from django.utils import timezone
from dashboard.models import LW321
from .models import UploadHistory
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, name='data_management.process_uploaded_data')
def process_uploaded_data_task(self, upload_history_id):
    """Process uploaded data in background after file is saved"""
    try:
        upload_history = UploadHistory.objects.get(id=upload_history_id)
        upload_history.status = 'processing'
        upload_history.save()
        
        logger.info(f"Starting data processing for upload ID: {upload_history_id}")
        
        from .utils import process_uploaded_file
        
        result = process_uploaded_file(upload_history)
        
        if result['success']:
            upload_history.status = 'completed'
            upload_history.total_rows = result['total_rows']
            upload_history.successful_rows = result['successful_rows']
            upload_history.failed_rows = result['failed_rows']
            upload_history.completed_at = timezone.now()
            if result.get('errors'):
                upload_history.error_log = '\n'.join(result['errors'])
            upload_history.save()
            
            logger.info(f"Data processing completed for upload ID: {upload_history_id}")
            return {
                'status': 'success',
                'total_rows': result['total_rows'],
                'successful_rows': result['successful_rows'],
                'failed_rows': result['failed_rows'],
            }
        else:
            upload_history.status = 'failed'
            upload_history.error_log = result.get('error', 'Unknown error')
            upload_history.save()
            
            logger.error(f"Data processing failed for upload ID: {upload_history_id}")
            return {
                'status': 'failed',
                'error': result.get('error', 'Unknown error')
            }
            
    except Exception as e:
        logger.exception(f"Error processing upload ID: {upload_history_id}")
        try:
            upload_history = UploadHistory.objects.get(id=upload_history_id)
            upload_history.status = 'failed'
            upload_history.error_log = str(e)
            upload_history.save()
        except:
            pass
        
        return {
            'status': 'error',
            'error': str(e)
        }


@shared_task(name='data_management.cleanup_old_uploads')
def cleanup_old_uploads():
    """
    Task untuk membersihkan file upload lama (opsional)
    Bisa dijadwalkan dengan celery beat
    """
    from datetime import timedelta
    cutoff_date = timezone.now() - timedelta(days=30)
    
    old_uploads = UploadHistory.objects.filter(
        created_at__lt=cutoff_date,
        status__in=['completed', 'failed']
    )
    
    count = old_uploads.count()
    old_uploads.delete()
    
    logger.info(f"Cleaned up {count} old upload records")
    return f"Cleaned up {count} old upload records"
