from django.db import models


class LW321(models.Model):
    """
    Model untuk menyimpan data pinjaman nasabah dengan 38 kolom sesuai kebutuhan
    """

    periode = models.CharField(max_length=30, db_index=True)
    kanca = models.CharField(max_length=150, blank=True)
    kode_uker = models.CharField(max_length=50, blank=True)
    uker = models.CharField(max_length=150, blank=True)
    ln_type = models.CharField(max_length=50, blank=True)
    nomor_rekening = models.CharField(max_length=50, unique=True, db_index=True)
    nama_debitur = models.CharField(max_length=200, blank=True)
    plafon = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    next_pmt_date = models.DateField(null=True, blank=True)
    next_int_pmt_date = models.DateField(null=True, blank=True)
    rate = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
    tgl_menunggak = models.DateField(null=True, blank=True)
    tgl_realisasi = models.DateField(null=True, blank=True)
    tgl_jatuh_tempo = models.DateField(null=True, blank=True)
    jangka_waktu = models.IntegerField(null=True, blank=True)
    flag_restruk = models.CharField(max_length=50, blank=True)
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
    kol_adk = models.CharField(max_length=50, blank=True)
    pn_pengelola_singlepn = models.CharField(max_length=150, blank=True)
    pn_pengelola_1 = models.CharField(max_length=150, blank=True)
    pn_pemrakarsa = models.CharField(max_length=150, blank=True)
    pn_referral = models.CharField(max_length=150, blank=True)
    pn_restruk = models.CharField(max_length=150, blank=True)
    pn_pengelola_2 = models.CharField(max_length=150, blank=True)
    pn_pemutus = models.CharField(max_length=150, blank=True)
    pn_crm = models.CharField(max_length=150, blank=True)
    pn_rm_referral_naik_segmentasi = models.CharField(max_length=150, blank=True)
    pn_rm_crr = models.CharField(max_length=150, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'LW321'
        verbose_name = 'LW321 data'
        verbose_name_plural = 'LW321 data'
        ordering = ['-periode', 'kanca', 'nomor_rekening']
        indexes = [
            models.Index(fields=['periode', 'kanca']),
            models.Index(fields=['periode', 'kolektibilitas_macet']),
            models.Index(fields=['nomor_rekening']),
        ]

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
