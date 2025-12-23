from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse
from .models import UploadHistory
from .forms import UploadDataForm
from .utils import process_uploaded_file, validate_file_structure
from dashboard.models import LW321


def admin_required(view_func):
    """
    Decorator untuk memastikan hanya admin yang bisa akses
    """
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_admin():
            messages.error(request, 'Anda tidak memiliki akses ke halaman ini.')
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def validate_upload_preview(request):
    """
    AJAX endpoint untuk validasi file dan preview 10 sample data
    Dipanggil saat user memilih file sebelum upload
    """
    if request.method == 'POST' and request.FILES.get('file'):
        upload_file = request.FILES['file']
        
        # Save temporary file
        import tempfile
        import os
        
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, upload_file.name)
        
        try:
            with open(temp_path, 'wb+') as destination:
                for chunk in upload_file.chunks():
                    destination.write(chunk)
            
            # Validate file structure
            validation_result = validate_file_structure(temp_path)
            
            # Cleanup
            os.remove(temp_path)
            os.rmdir(temp_dir)
            
            return JsonResponse(validation_result)
            
        except Exception as e:
            # Cleanup on error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
            
            return JsonResponse({
                'valid': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'valid': False,
        'error': 'No file provided'
    })


@admin_required
def upload_data_view(request):
    """
    View untuk upload data (hanya admin)
    Upload file langsung, processing dijalankan di background dengan Celery
    """
    if request.method == 'POST':
        form = UploadDataForm(request.POST, request.FILES)
        if form.is_valid():
            upload_file = request.FILES['file']
            
            # Simpan upload history dengan status 'queued'
            upload_history = UploadHistory.objects.create(
                uploaded_by=request.user,
                file_name=upload_file.name,
                file_path=upload_file,
                file_size=upload_file.size,
                status='queued',  # Changed from 'pending' to 'queued'
                notes=form.cleaned_data.get('notes', ''),
            )
            
            # Queue task untuk diproses di background
            try:
                from .tasks import process_uploaded_data_task
                
                # Jalankan task secara asynchronous
                task = process_uploaded_data_task.delay(upload_history.id)
                
                messages.success(
                    request, 
                    f'File "{upload_file.name}" berhasil diupload! '
                    f'Data sedang diproses di background. '
                    f'Silakan cek halaman History untuk melihat status.'
                )
                
            except Exception as e:
                upload_history.status = 'failed'
                upload_history.error_log = f'Failed to queue task: {str(e)}'
                upload_history.save()
                
                messages.error(
                    request, 
                    f'Gagal menambahkan file ke antrian: {str(e)}. '
                    f'Pastikan Redis dan Celery worker sudah berjalan.'
                )
            
            return redirect('data_management:upload_history')
    else:
        form = UploadDataForm()
    
    # Get statistics for display - Daftar Tanggal yang Tersedia (lebih informatif)
    from django.db.models import Count, Min, Max
    
    # Get all available dates with record count
    date_stats = LW321.objects.values('periode').annotate(
        record_count=Count('id'),
        unique_customers=Count('cif_no', distinct=True),
        unique_ukers=Count('kode_uker', distinct=True)
    ).order_by('-periode')
    
    total_records = LW321.objects.count()
    total_dates = date_stats.count()
    
    # Get date range
    if date_stats.exists():
        oldest_date = date_stats.last()['periode']
        newest_date = date_stats.first()['periode']
    else:
        oldest_date = None
        newest_date = None
    
    context = {
        'form': form,
        'page_title': 'Upload Data',
        'date_stats': date_stats,  # Daftar tanggal yang tersedia dengan detail
        'total_records': total_records,
        'total_dates': total_dates,
        'oldest_date': oldest_date,
        'newest_date': newest_date,
    }
    return render(request, 'data_management/upload_data.html', context)


@admin_required
def upload_history_view(request):
    """
    View untuk melihat riwayat upload (hanya admin)
    """
    uploads = UploadHistory.objects.all().select_related('uploaded_by')
    
    # Pagination
    paginator = Paginator(uploads, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'page_title': 'History Data',
    }
    return render(request, 'data_management/upload_history.html', context)


@admin_required
def delete_data_view(request):
    """
    View untuk delete data (hanya admin)
    """
    if request.method == 'POST':
        # Implementasi delete data berdasarkan periode (tanggal)
        delete_type = request.POST.get('delete_type')
        
        try:
            if delete_type == 'by_date':
                # Hapus berdasarkan tanggal
                selected_date = request.POST.get('selected_date')
                
                if not selected_date:
                    messages.error(request, 'Tanggal harus dipilih.')
                    return redirect('data_management:delete_data')
                
                # Convert format dari YYYY-MM-DD ke DD/MM/YYYY (format di database)
                from datetime import datetime
                date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
                periode_str = date_obj.strftime('%d/%m/%Y')
                
                # Hapus data dengan periode tersebut
                deleted_count = LW321.objects.filter(periode=periode_str).delete()[0]
                
                if deleted_count > 0:
                    messages.success(request, f'Berhasil menghapus {deleted_count} record dengan tanggal {periode_str}.')
                else:
                    messages.warning(request, f'Tidak ada data dengan tanggal {periode_str}.')
                    
            elif delete_type == 'by_range':
                # Hapus berdasarkan range tanggal
                date_from = request.POST.get('date_from')
                date_to = request.POST.get('date_to')
                
                if not date_from or not date_to:
                    messages.error(request, 'Tanggal mulai dan tanggal akhir harus dipilih.')
                    return redirect('data_management:delete_data')
                
                from datetime import datetime
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                
                # Get all unique periode dalam range
                all_periods = LW321.objects.values_list('periode', flat=True).distinct()
                periods_to_delete = []
                
                for periode in all_periods:
                    try:
                        periode_date = datetime.strptime(periode, '%d/%m/%Y')
                        if date_from_obj <= periode_date <= date_to_obj:
                            periods_to_delete.append(periode)
                    except:
                        continue
                
                if periods_to_delete:
                    deleted_count = LW321.objects.filter(periode__in=periods_to_delete).delete()[0]
                    messages.success(request, f'Berhasil menghapus {deleted_count} record dari tanggal {date_from} sampai {date_to}.')
                else:
                    messages.warning(request, f'Tidak ada data dalam range tanggal tersebut.')
                    
            elif delete_type == 'all':
                # Hapus semua data (dengan konfirmasi)
                confirm = request.POST.get('confirm_delete_all')
                
                if confirm == 'DELETE ALL DATA':
                    deleted_count = LW321.objects.all().delete()[0]
                    messages.success(request, f'Berhasil menghapus semua data ({deleted_count} record).')
                else:
                    messages.error(request, 'Konfirmasi tidak sesuai. Data tidak dihapus.')
            else:
                messages.error(request, 'Tipe penghapusan tidak valid.')
                
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
        
        return redirect('data_management:delete_data')
    
    # Get available dates for dropdown
    from django.db.models import Count
    available_dates = LW321.objects.values('periode').annotate(
        count=Count('id')
    ).order_by('-periode')[:50]
    
    context = {
        'page_title': 'Delete Data',
        'available_dates': available_dates,
        'total_records': LW321.objects.count(),
    }
    return render(request, 'data_management/delete_data.html', context)


@admin_required
def view_all_data_view(request):
    """Display an overview of LW321 for administrators."""

    loans = LW321.objects.all().order_by('-periode', 'kanca', 'nomor_rekening')[:100]
    columns = [
        'periode',
        'kanca',
        'nomor_rekening',
        'nama_debitur',
        'plafon',
        'kolektibilitas_macet',
        'flag_restruk',
    ]

    column_labels = {
        'periode': 'Periode',
        'kanca': 'Kanca',
        'nomor_rekening': 'Nomor Rekening',
        'nama_debitur': 'Nama Debitur',
        'plafon': 'Plafon',
        'kolektibilitas_macet': 'Kolektibilitas Macet',
        'flag_restruk': 'Flag Restruk',
    }
    headers = [(column, column_labels.get(column, column.replace('_', ' ').title())) for column in columns]

    rows = []
    for loan in loans:
        rows.append([getattr(loan, column) for column in columns])

    context = {
        'page_title': 'View All Data',
        'loans': loans,
        'columns': columns,
        'headers': headers,
        'rows': rows,
    }
    return render(request, 'data_management/view_all_data.html', context)
