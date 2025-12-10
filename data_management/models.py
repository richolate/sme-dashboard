from django.db import models
from accounts.models import User


class UploadHistory(models.Model):
    """
    Model untuk menyimpan riwayat upload data
    """
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploads')
    file_name = models.CharField(max_length=255)
    file_path = models.FileField(upload_to='uploads/%Y/%m/%d/')
    file_size = models.BigIntegerField()  # in bytes
    total_rows = models.IntegerField(default=0)
    successful_rows = models.IntegerField(default=0)
    failed_rows = models.IntegerField(default=0)
    
    STATUS_CHOICES = (
        ('queued', 'Queued'),  # File uploaded, waiting in queue
        ('processing', 'Processing'),  # Currently being processed
        ('completed', 'Completed'),  # Successfully completed
        ('failed', 'Failed'),  # Processing failed
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    
    error_log = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'upload_history'
        verbose_name = 'Upload History'
        verbose_name_plural = 'Upload Histories'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.file_name} - {self.uploaded_by.username} - {self.created_at}"
