from django.contrib import admin
from .models import LoanData, ProcessedData


@admin.register(LoanData)
class LoanDataAdmin(admin.ModelAdmin):
    list_display = (
        'nomor_rekening',
        'nama_debitur',
        'periode',
        'kanca',
        'plafon',
        'kolektibilitas_lancar',
        'updated_at',
    )
    list_filter = (
        'periode',
        'kanca',
        'kolektibilitas_lancar',
        'kolektibilitas_macet',
    )
    search_fields = (
        'nomor_rekening',
        'nama_debitur',
        'cif_no',
        'code',
        'description',
    )
    date_hierarchy = 'next_pmt_date'
    list_per_page = 50


@admin.register(ProcessedData)
class ProcessedDataAdmin(admin.ModelAdmin):
    list_display = ('data_type', 'sub_type', 'date', 'created_at')
    list_filter = ('data_type', 'sub_type', 'date')
    search_fields = ('data_type', 'sub_type')
    date_hierarchy = 'date'
