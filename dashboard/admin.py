from django.contrib import admin
from .models import LW321, ProcessedData, KomitmenUpload, KomitmenData


@admin.register(LW321)
class LW321Admin(admin.ModelAdmin):
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
    # date_hierarchy dihapus karena next_pmt_date sudah jadi CharField
    list_per_page = 50


@admin.register(ProcessedData)
class ProcessedDataAdmin(admin.ModelAdmin):
    list_display = ('data_type', 'sub_type', 'date', 'created_at')
    list_filter = ('data_type', 'sub_type', 'date')
    search_fields = ('data_type', 'sub_type')
    date_hierarchy = 'date'


@admin.register(KomitmenUpload)
class KomitmenUploadAdmin(admin.ModelAdmin):
    list_display = ('periode_display', 'file_name', 'row_count', 'status', 'uploaded_by', 'uploaded_at')
    list_filter = ('status', 'periode')
    search_fields = ('file_name', 'notes')
    readonly_fields = ('uploaded_at', 'uploaded_by', 'row_count')
    date_hierarchy = 'periode'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Jika object baru
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(KomitmenData)
class KomitmenDataAdmin(admin.ModelAdmin):
    list_display = ('nama_uker', 'kode_uker', 'periode', 'nama_kanca', 'kur_os', 'small_os', 'created_at')
    list_filter = ('periode', 'kode_kanca')
    search_fields = ('nama_uker', 'kode_uker', 'nama_kanca', 'kode_kanca')
    date_hierarchy = 'periode'
    list_per_page = 50
