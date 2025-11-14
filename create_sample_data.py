"""
Script untuk membuat sample data untuk testing dashboard
Jalankan: python create_sample_data.py
"""

import os
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from dashboard.models import LoanData
from accounts.models import User


def create_sample_users():
    """Buat sample users"""
    print("Creating sample users...")
    
    # Admin user
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@bri.co.id',
            password='admin123',
            first_name='Admin',
            last_name='System',
            role='admin'
        )
        print(f"✅ Created admin user: {admin.username}")
    
    # Regular user
    if not User.objects.filter(username='user1').exists():
        user = User.objects.create_user(
            username='user1',
            email='user1@bri.co.id',
            password='user123',
            first_name='User',
            last_name='Test',
            role='user'
        )
        print(f"✅ Created regular user: {user.username}")


def create_sample_LW321(num_records=100):
    """Buat sample LW321"""
    print(f"\nCreating {num_records} sample loan records...")
    
    periodes = ['2023-12', '2024-01', '2024-02', '2024-03']
    kanca_list = ['Jakarta Pusat', 'Jakarta Selatan', 'Jakarta Timur', 'Jakarta Barat', 'Jakarta Utara']
    uker_list = ['Unit 1', 'Unit 2', 'Unit 3', 'Unit 4']
    ln_types = ['KUR', 'Kupedes', 'Kupedes Mikro', 'Kupedes Menengah']
    flag_restruk_choices = ['Ya', 'Tidak']
    pn_names = ['Andi Pratama', 'Budi Santoso', 'Citra Lestari', 'Dewi Kusuma', 'Eka Putra']
    
    created_count = 0
    
    for i in range(num_records):
        try:
            # Random date dalam 30 hari terakhir
            days_ago = random.randint(0, 30)
            loan_date = datetime.now().date() - timedelta(days=days_ago)
            
            plafon_value = Decimal(random.randint(50, 500)) * Decimal('1000000')  # 50 juta - 500 juta
            jangka_waktu = random.choice([12, 24, 36, 48, 60])
            flag_restruk = random.choice(flag_restruk_choices)
            kolektibilitas = random.choice(['Lancar', 'DPK', 'Kurang Lancar', 'Diragukan', 'Macet'])
            tgl_realisasi = loan_date
            tgl_jatuh_tempo = tgl_realisasi + timedelta(days=30 * (jangka_waktu // 12))
            tunggakan_multiplier = Decimal(random.choice([0, 0, 0, 5, 10, 15]))

            LoanData.objects.create(
                periode=random.choice(periodes),
                kanca=random.choice(kanca_list),
                kode_uker=f"UK{str(random.randint(1, 999)).zfill(3)}",
                uker=random.choice(uker_list),
                ln_type=random.choice(ln_types),
                nomor_rekening=f"30{str(i+1).zfill(8)}",
                nama_debitur=f"Debitur {i + 1}",
                plafon=plafon_value,
                next_pmt_date=tgl_realisasi + timedelta(days=30),
                next_int_pmt_date=tgl_realisasi + timedelta(days=15),
                rate=Decimal(random.randrange(600, 1500)) / Decimal('100'),
                tgl_menunggak=(tgl_realisasi + timedelta(days=random.randint(60, 120))) if flag_restruk == 'Ya' else None,
                tgl_realisasi=tgl_realisasi,
                tgl_jatuh_tempo=tgl_jatuh_tempo,
                jangka_waktu=jangka_waktu,
                flag_restruk=flag_restruk,
                cif_no=f"CIF{str(i+1).zfill(6)}",
                kolektibilitas_lancar='1' if kolektibilitas == 'Lancar' else '0',
                kolektibilitas_dpk='1' if kolektibilitas == 'DPK' else '0',
                kolektibilitas_kurang_lancar='1' if kolektibilitas == 'Kurang Lancar' else '0',
                kolektibilitas_diragukan='1' if kolektibilitas == 'Diragukan' else '0',
                kolektibilitas_macet='1' if kolektibilitas == 'Macet' else '0',
                tunggakan_pokok=plafon_value * tunggakan_multiplier / Decimal('100'),
                tunggakan_bunga=plafon_value * tunggakan_multiplier / Decimal('200'),
                tunggakan_pinalti=plafon_value * tunggakan_multiplier / Decimal('500'),
                code=f"CD{random.randint(100, 999)}",
                description=f"Produk {kolektibilitas}",
                kol_adk=f"KOL{random.randint(1, 5)}",
                pn_pengelola_singlepn=random.choice(pn_names),
                pn_pengelola_1=random.choice(pn_names),
                pn_pemrakarsa=random.choice(pn_names),
                pn_referral=random.choice(pn_names),
                pn_restruk=random.choice(pn_names),
                pn_pengelola_2=random.choice(pn_names),
                pn_pemutus=random.choice(pn_names),
                pn_crm=random.choice(pn_names),
                pn_rm_referral_naik_segmentasi=random.choice(pn_names),
                pn_rm_crr=random.choice(pn_names),
            )
            created_count += 1
            
            if (i + 1) % 20 == 0:
                print(f"  Created {i + 1} records...")
                
        except Exception as e:
            print(f"❌ Error creating record {i+1}: {e}")
    
    print(f"✅ Successfully created {created_count} loan records")


def show_statistics():
    """Tampilkan statistik data"""
    print("\n" + "=" * 60)
    print("Database Statistics")
    print("=" * 60)
    
    # Users
    admin_count = User.objects.filter(role='admin').count()
    user_count = User.objects.filter(role='user').count()
    print(f"\nUsers:")
    print(f"  Admin users: {admin_count}")
    print(f"  Regular users: {user_count}")
    print(f"  Total users: {admin_count + user_count}")
    
    # LW321
    total_loans = LoanData.objects.count()
    total_amount = LoanData.objects.aggregate(
        total=django.db.models.Sum('plafon')
    )['total'] or 0
    
    print(f"\nLW321:")
    print(f"  Total records: {total_loans}")
    print(f"  Total plafon: Rp {total_amount:,.0f}")
    
    if total_loans > 0:
        by_kanca = LoanData.objects.values('kanca').annotate(
            count=django.db.models.Count('id')
        )
        print(f"\n  By Kanca:")
        for item in by_kanca:
            print(f"    - {item['kanca']}: {item['count']} records")
        
        by_flag = LoanData.objects.values('flag_restruk').annotate(
            count=django.db.models.Count('id')
        )
        print(f"\n  By Flag Restruk:")
        for item in by_flag:
            print(f"    - {item['flag_restruk']}: {item['count']} records")
    
    print("\n" + "=" * 60)
    print("✅ Sample data creation completed!")
    print("=" * 60)
    print("\nYou can now:")
    print("1. Run the server: python manage.py runserver")
    print("2. Login with:")
    print("   - Admin: username=admin, password=admin123")
    print("   - User:  username=user1, password=user123")
    print("=" * 60)


if __name__ == "__main__":
    print("=" * 60)
    print("Creating Sample Data for Dashboard")
    print("=" * 60)
    
    create_sample_users()
    create_sample_LW321(100)  # Buat 100 sample records
    show_statistics()
