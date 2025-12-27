from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class LW321(models.Model):
    """
    Model untuk menyimpan data pinjaman nasabah dengan 38 kolom sesuai kebutuhan
    """

    periode = models.CharField(max_length=20, db_index=True)  # Diubah dari 30 ke 20
    kanca = models.CharField(max_length=100, blank=True)  # Diubah dari 50 ke 100 untuk keamanan
    kode_uker = models.CharField(max_length=10, blank=True)  # Diubah dari 50 ke 10
    uker = models.CharField(max_length=100, blank=True)  # Diubah dari 50 ke 100 untuk keamanan
    ln_type = models.CharField(max_length=10, blank=True)  # Diubah dari 50 ke 10
    nomor_rekening = models.CharField(max_length=100, db_index=True)  # Diubah dari 50 ke 100 untuk keamanan
    nama_debitur = models.CharField(max_length=100, blank=True)  # Diubah dari 50 ke 100 untuk keamanan
    plafon = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    next_pmt_date = models.CharField(max_length=20, null=True, blank=True)  # Diubah dari DateField ke CharField
    next_int_pmt_date = models.CharField(max_length=20, null=True, blank=True)  # Diubah dari DateField ke CharField
    rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Diubah dari (7,4) ke (5,2)
    tgl_menunggak = models.CharField(max_length=20, null=True, blank=True)  # Diubah dari DateField ke CharField
    tgl_realisasi = models.CharField(max_length=20, null=True, blank=True)  # Diubah dari DateField ke CharField
    tgl_jatuh_tempo = models.CharField(max_length=20, null=True, blank=True)  # Diubah dari DateField ke CharField
    jangka_waktu = models.CharField(max_length=10, null=True, blank=True)  # Diubah dari IntegerField ke CharField (contoh: 106M)
    flag_restruk = models.CharField(max_length=10, blank=True)  # Diubah dari 50 ke 10
    cif_no = models.CharField(max_length=100, blank=True)  # Diubah dari 50 ke 100 untuk keamanan
    kolektibilitas_lancar = models.CharField(max_length=100, blank=True)  # Diubah dari 50 ke 100 untuk keamanan
    kolektibilitas_dpk = models.CharField(max_length=100, blank=True)  # Diubah dari 50 ke 100 untuk keamanan
    kolektibilitas_kurang_lancar = models.CharField(max_length=100, blank=True)  # Diubah dari 50 ke 100 untuk keamanan
    kolektibilitas_diragukan = models.CharField(max_length=100, blank=True)  # Diubah dari 50 ke 100 untuk keamanan
    kolektibilitas_macet = models.CharField(max_length=100, blank=True)  # Diubah dari 50 ke 100 untuk keamanan
    tunggakan_pokok = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    tunggakan_bunga = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    tunggakan_pinalti = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    code = models.CharField(max_length=100, blank=True)  # Diubah dari 50 ke 100 untuk keamanan
    description = models.CharField(max_length=255, blank=True)
    kol_adk = models.CharField(max_length=10, blank=True)  # Diubah dari 50 ke 10
    pn_rm = models.CharField(max_length=20, blank=True)  # Diubah dari 150 ke 20
    nama_rm = models.CharField(max_length=100, blank=True)  # Diubah dari 50 ke 100 untuk keamanan
    os = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)  # OS kolom baru
    nasabah = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)  # NASABAH (angka)
    dub_nasabah = models.CharField(max_length=10, null=True, blank=True)  # DUB NASABAH - VARCHAR untuk simpan "TRUE"/"FALSE"

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lw321'
        verbose_name = 'LW321 data'
        verbose_name_plural = 'LW321 data'
        ordering = ['-periode', 'kanca', 'nomor_rekening']
        indexes = [
            models.Index(fields=['periode', 'kanca']),
            models.Index(fields=['periode', 'kolektibilitas_macet']),
            models.Index(fields=['nomor_rekening']),
            models.Index(fields=['periode', 'nomor_rekening']),
        ]
        # Tidak ada unique constraint - nomor_rekening boleh duplikat untuk tanggal berbeda

    def __str__(self):
        nama = self.nama_debitur or '-'
        return f"{self.nomor_rekening} - {nama}"


class ProcessedData(models.Model):
    """
    Model untuk menyimpan data yang sudah diolah untuk dashboard
    """
    data_type = models.CharField(max_length=50, db_index=True)  # os, summary, grafik_harian
    sub_type = models.CharField(max_length=50, blank=True)  # medium_only, konsol, only
    date = models.DateField(db_index=True)
    
    # Data yang sudah diolah disimpan dalam JSON atau field terpisah
    processed_json = models.JSONField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'processed_data'
        verbose_name = 'Processed Data'
        verbose_name_plural = 'Processed Data'
        ordering = ['-date']
        unique_together = ['data_type', 'sub_type', 'date']
    
    def __str__(self):
        return f"{self.data_type} - {self.date}"


class KomitmenUpload(models.Model):
    """
    Model untuk tracking history upload file komitmen
    """
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    periode = models.DateField(unique=True, db_index=True, help_text="Periode bulan komitmen (contoh: 2025-11-01)")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=255, help_text="Nama file yang diupload")
    row_count = models.IntegerField(default=0, help_text="Jumlah baris data (tidak termasuk total row)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    notes = models.TextField(blank=True, help_text="Catatan validasi atau error messages")
    
    class Meta:
        db_table = 'komitmen_upload'
        verbose_name = 'Komitmen Upload'
        verbose_name_plural = 'Komitmen Uploads'
        ordering = ['-periode']
    
    def __str__(self):
        return f"Komitmen {self.periode.strftime('%B %Y')} - {self.status}"
    
    def periode_display(self):
        """Return formatted periode for display"""
        months = {
            1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April',
            5: 'Mei', 6: 'Juni', 7: 'Juli', 8: 'Agustus',
            9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
        }
        return f"{months[self.periode.month]} {self.periode.year}"


class KomitmenData(models.Model):
    """
    Model untuk menyimpan data komitmen per uker
    1 row = 1 uker dengan semua produk (KUR, SMALL, KECIL NCC, KECIL CC)
    """
    upload = models.ForeignKey(KomitmenUpload, on_delete=models.CASCADE, related_name='data')
    periode = models.DateField(db_index=True, help_text="Periode bulan komitmen")
    
    # Identifiers
    kode_kanca = models.IntegerField(db_index=True, help_text="Kode KANCA sebagai integer")
    kode_uker = models.CharField(max_length=20, db_index=True)
    nama_kanca = models.CharField(max_length=100)
    nama_uker = models.CharField(max_length=100)
    
    # KUR RITEL - bisa angka, 0, atau NULL (untuk - atau kosong)
    # Decimal(20, 10) untuk presisi tinggi (contoh: 191954.5908991)
    kur_deb = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    kur_os = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    kur_pl = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    kur_npl = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    kur_dpk = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    
    # SMALL SD 5M
    small_deb = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    small_os = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    small_pl = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    small_npl = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    small_dpk = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    
    # KECIL NCC
    kecil_ncc_deb = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    kecil_ncc_os = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    kecil_ncc_pl = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    kecil_ncc_npl = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    kecil_ncc_dpk = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    
    # KECIL CC
    kecil_cc_deb = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    kecil_cc_os = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    kecil_cc_pl = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    kecil_cc_npl = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    kecil_cc_dpk = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'komitmen_data'
        verbose_name = 'Komitmen Data'
        verbose_name_plural = 'Komitmen Data'
        unique_together = ['periode', 'kode_uker']
        indexes = [
            models.Index(fields=['periode', 'kode_uker']),
            models.Index(fields=['periode', 'kode_kanca']),
        ]
        ordering = ['kode_kanca', 'kode_uker']
    
    def __str__(self):
        return f"{self.nama_uker} - {self.periode.strftime('%b %Y')}"
