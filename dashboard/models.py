from django.db import models


class LW321(models.Model):
    """
    Model untuk menyimpan data pinjaman nasabah dengan 38 kolom sesuai kebutuhan
    """

    periode = models.CharField(max_length=20, db_index=True)  # Diubah dari 30 ke 20
    kanca = models.CharField(max_length=50, blank=True)  # Diubah dari 150 ke 50
    kode_uker = models.CharField(max_length=10, blank=True)  # Diubah dari 50 ke 10
    uker = models.CharField(max_length=50, blank=True)  # Diubah dari 150 ke 50
    ln_type = models.CharField(max_length=10, blank=True)  # Diubah dari 50 ke 10
    nomor_rekening = models.CharField(max_length=50, db_index=True)
    nama_debitur = models.CharField(max_length=50, blank=True)  # Diubah dari 200 ke 50
    plafon = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    next_pmt_date = models.CharField(max_length=20, null=True, blank=True)  # Diubah dari DateField ke CharField
    next_int_pmt_date = models.CharField(max_length=20, null=True, blank=True)  # Diubah dari DateField ke CharField
    rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Diubah dari (7,4) ke (5,2)
    tgl_menunggak = models.CharField(max_length=20, null=True, blank=True)  # Diubah dari DateField ke CharField
    tgl_realisasi = models.CharField(max_length=20, null=True, blank=True)  # Diubah dari DateField ke CharField
    tgl_jatuh_tempo = models.CharField(max_length=20, null=True, blank=True)  # Diubah dari DateField ke CharField
    jangka_waktu = models.CharField(max_length=10, null=True, blank=True)  # Diubah dari IntegerField ke CharField (contoh: 106M)
    flag_restruk = models.CharField(max_length=10, blank=True)  # Diubah dari 50 ke 10
    cif_no = models.CharField(max_length=50, blank=True)
    kolektibilitas_lancar = models.CharField(max_length=50, blank=True)
    kolektibilitas_dpk = models.CharField(max_length=50, blank=True)
    kolektibilitas_kurang_lancar = models.CharField(max_length=50, blank=True)
    kolektibilitas_diragukan = models.CharField(max_length=50, blank=True)
    kolektibilitas_macet = models.CharField(max_length=50, blank=True)
    tunggakan_pokok = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    tunggakan_bunga = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    tunggakan_pinalti = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    code = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=255, blank=True)
    kol_adk = models.CharField(max_length=10, blank=True)  # Diubah dari 50 ke 10
    pn_rm = models.CharField(max_length=20, blank=True)  # Diubah dari 150 ke 20
    nama_rm = models.CharField(max_length=50, blank=True)  # Diubah dari 150 ke 50
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
