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
    """Decorator to ensure only admin users can access"""
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_admin():
            messages.error(request, 'Anda tidak memiliki akses ke halaman ini.')
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def validate_upload_preview(request):
    """AJAX endpoint for file validation and preview of 10 sample data"""
    if request.method == 'POST' and request.FILES.get('file'):
        upload_file = request.FILES['file']
        
        import tempfile
        import os
        
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, upload_file.name)
        
        try:
            with open(temp_path, 'wb+') as destination:
                for chunk in upload_file.chunks():
                    destination.write(chunk)
            
            validation_result = validate_file_structure(temp_path)
            
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
    """Display an overview of LW321 for administrators with filtering and pagination."""
    from django.core.paginator import Paginator
    from django.db.models import Q
    
    # Get all available periods
    available_periods = LW321.objects.values_list('periode', flat=True).distinct().order_by('-periode')
    
    # Get selected period from request
    selected_periode = request.GET.get('periode', '')
    search_query = request.GET.get('search', '').strip()
    page_number = request.GET.get('page', 1)
    
    # Base queryset
    loans_query = LW321.objects.all()
    
    # Filter by periode if selected
    if selected_periode:
        loans_query = loans_query.filter(periode=selected_periode)
    
    # Search functionality
    if search_query:
        loans_query = loans_query.filter(
            Q(nomor_rekening__icontains=search_query) |
            Q(nama_debitur__icontains=search_query) |
            Q(kanca__icontains=search_query) |
            Q(uker__icontains=search_query) |
            Q(kode_uker__icontains=search_query) |
            Q(cif_no__icontains=search_query) |
            Q(pn_rm__icontains=search_query) |
            Q(nama_rm__icontains=search_query)
        )
    
    # Order by
    loans_query = loans_query.order_by('-periode', 'kanca', 'nomor_rekening')
    
    # Pagination (100 rows per page)
    paginator = Paginator(loans_query, 100)
    loans_page = paginator.get_page(page_number)
    
    # All columns from LW321 model
    columns = [
        'periode', 'kanca', 'kode_uker', 'uker', 'ln_type', 'nomor_rekening',
        'nama_debitur', 'plafon', 'next_pmt_date', 'next_int_pmt_date', 'rate',
        'tgl_menunggak', 'tgl_realisasi', 'tgl_jatuh_tempo', 'jangka_waktu',
        'flag_restruk', 'cif_no', 'kolektibilitas_lancar', 'kolektibilitas_dpk',
        'kolektibilitas_kurang_lancar', 'kolektibilitas_diragukan', 'kolektibilitas_macet',
        'tunggakan_pokok', 'tunggakan_bunga', 'tunggakan_pinalti', 'code',
        'description', 'kol_adk', 'pn_rm', 'nama_rm', 'os', 'nasabah', 'dub_nasabah'
    ]
    
    column_labels = {
        'periode': 'Periode',
        'kanca': 'Kanca',
        'kode_uker': 'Kode Uker',
        'uker': 'Uker',
        'ln_type': 'LN Type',
        'nomor_rekening': 'Nomor Rekening',
        'nama_debitur': 'Nama Debitur',
        'plafon': 'Plafon',
        'next_pmt_date': 'Next PMT Date',
        'next_int_pmt_date': 'Next Int PMT Date',
        'rate': 'Rate',
        'tgl_menunggak': 'Tgl Menunggak',
        'tgl_realisasi': 'Tgl Realisasi',
        'tgl_jatuh_tempo': 'Tgl Jatuh Tempo',
        'jangka_waktu': 'Jangka Waktu',
        'flag_restruk': 'Flag Restruk',
        'cif_no': 'CIF No',
        'kolektibilitas_lancar': 'Kol Lancar',
        'kolektibilitas_dpk': 'Kol DPK',
        'kolektibilitas_kurang_lancar': 'Kol Kurang Lancar',
        'kolektibilitas_diragukan': 'Kol Diragukan',
        'kolektibilitas_macet': 'Kol Macet',
        'tunggakan_pokok': 'Tunggakan Pokok',
        'tunggakan_bunga': 'Tunggakan Bunga',
        'tunggakan_pinalti': 'Tunggakan Pinalti',
        'code': 'Code',
        'description': 'Description',
        'kol_adk': 'Kol ADK',
        'pn_rm': 'PN RM',
        'nama_rm': 'Nama RM',
        'os': 'OS',
        'nasabah': 'Nasabah',
        'dub_nasabah': 'Dub Nasabah',
    }
    
    headers = [(column, column_labels.get(column, column.replace('_', ' ').title())) for column in columns]
    
    context = {
        'page_title': 'View All Data',
        'loans_page': loans_page,
        'columns': columns,
        'headers': headers,
        'available_periods': available_periods,
        'selected_periode': selected_periode,
        'search_query': search_query,
        'total_count': paginator.count,
    }
    return render(request, 'data_management/view_all_data.html', context)


# ==================== KOMITMEN VIEWS ====================

@admin_required
def validate_komitmen_ajax(request):
    """AJAX endpoint for komitmen file validation"""
    if request.method == 'POST' and request.FILES.get('file'):
        from .validators import validate_komitmen_excel
        import tempfile
        import os
        
        upload_file = request.FILES['file']
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, upload_file.name)
        
        try:
            with open(temp_path, 'wb+') as destination:
                for chunk in upload_file.chunks():
                    destination.write(chunk)
            
            validation_result = validate_komitmen_excel(temp_path)
            
            # Cleanup temp file
            os.remove(temp_path)
            os.rmdir(temp_dir)
            
            # Format periode for display
            if validation_result['periode']:
                periode_str = validation_result['periode'].strftime('%B %Y')
            else:
                periode_str = None
            
            # Format preview rows for JSON
            preview_rows = validation_result.get('preview_rows', [])
            formatted_preview = []
            for row in preview_rows:
                formatted_preview.append({
                    'kode_kanca': row['kode_kanca'],
                    'kode_uker': row['kode_uker'],
                    'nama_kanca': row['nama_kanca'],
                    'nama_uker': row['nama_uker'],
                    'kur_os': f"{row['kur_os']:,.0f}" if row['kur_os'] else '-',
                    'small_os': f"{row['small_os']:,.0f}" if row['small_os'] else '-',
                    'kecil_ncc_os': f"{row['kecil_ncc_os']:,.0f}" if row['kecil_ncc_os'] else '-',
                    'kecil_cc_os': f"{row['kecil_cc_os']:,.0f}" if row['kecil_cc_os'] else '-',
                })
            
            return JsonResponse({
                'valid': validation_result['valid'],
                'errors': validation_result['errors'],
                'warnings': validation_result['warnings'],
                'data_row_count': validation_result['data_row_count'],
                'total_row_count': validation_result['total_row_count'],
                'periode': periode_str,
                'preview_rows': formatted_preview,
            })
            
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
            
            return JsonResponse({
                'valid': False,
                'errors': [f'Error: {str(e)}'],
                'warnings': [],
                'data_row_count': 0,
                'total_row_count': 0,
                'periode': None,
            })
    
    return JsonResponse({'valid': False, 'errors': ['Invalid request'], 'warnings': []})


@admin_required
def upload_komitmen(request):
    """Upload komitmen file - Step 1: Validate and show preview"""
    from .forms import KomitmenUploadForm
    from .validators import validate_komitmen_excel
    from .utils import compare_komitmen_data
    import tempfile
    import os
    
    if request.method == 'POST':
        form = KomitmenUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            upload_file = request.FILES['file']
            notes = form.cleaned_data.get('notes', '')
            
            # Save to temp file
            temp_dir = tempfile.mkdtemp()
            temp_path = os.path.join(temp_dir, upload_file.name)
            
            try:
                with open(temp_path, 'wb+') as destination:
                    for chunk in upload_file.chunks():
                        destination.write(chunk)
                
                # Validate
                validation_result = validate_komitmen_excel(temp_path)
                
                if not validation_result['valid']:
                    # Cleanup
                    os.remove(temp_path)
                    os.rmdir(temp_dir)
                    
                    for error in validation_result['errors']:
                        messages.error(request, error)
                    
                    return render(request, 'data_management/upload_komitmen.html', {
                        'page_title': 'Upload Komitmen',
                        'form': form,
                    })
                
                # Compare with existing data
                compare_result = compare_komitmen_data(
                    validation_result['data_df'],
                    validation_result['periode']
                )
                
                # Save temp file path and validation result to session
                request.session['komitmen_temp_file'] = temp_path
                request.session['komitmen_filename'] = upload_file.name
                request.session['komitmen_notes'] = notes
                request.session['komitmen_periode'] = validation_result['periode'].isoformat()
                
                # Redirect to preview
                return redirect('data_management:preview_komitmen')
                
            except Exception as e:
                # Cleanup on error
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                if os.path.exists(temp_dir):
                    os.rmdir(temp_dir)
                
                messages.error(request, f'Error saat memproses file: {str(e)}')
                return render(request, 'data_management/upload_komitmen.html', {
                    'page_title': 'Upload Komitmen',
                    'form': form,
                })
    
    else:
        form = KomitmenUploadForm()
    
    context = {
        'page_title': 'Upload Komitmen',
        'form': form,
    }
    return render(request, 'data_management/upload_komitmen.html', context)


@admin_required
def preview_komitmen(request):
    """Preview komitmen upload - Step 2: Show validation results and changes"""
    from .validators import validate_komitmen_excel, COLUMN_INDICES, clean_numeric_value
    from .utils import compare_komitmen_data
    from datetime import datetime
    import os
    import pandas as pd
    
    temp_file = request.session.get('komitmen_temp_file')
    filename = request.session.get('komitmen_filename')
    notes = request.session.get('komitmen_notes', '')
    periode_str = request.session.get('komitmen_periode')
    
    if not temp_file or not os.path.exists(temp_file):
        messages.error(request, 'Session expired. Silakan upload ulang.')
        return redirect('data_management:upload_komitmen')
    
    try:
        periode = datetime.fromisoformat(periode_str).date()
        
        # Re-validate (to get fresh data)
        validation_result = validate_komitmen_excel(temp_file, periode)
        
        if not validation_result['valid']:
            messages.error(request, 'File tidak valid.')
            return redirect('data_management:upload_komitmen')
        
        # Compare with existing data
        compare_result = compare_komitmen_data(
            validation_result['data_df'],
            periode
        )
        
        # Prepare ALL data for preview (not just 10 rows)
        from .validators import COLUMN_INDICES
        all_preview_data = []
        for _, row in validation_result['data_df'].iterrows():
            # Clean kode_kanca (remove .0 from float)
            kode_kanca_raw = str(row[COLUMN_INDICES['kode_kanca']]).strip()
            try:
                kode_kanca = str(int(float(kode_kanca_raw)))
            except (ValueError, TypeError):
                kode_kanca = kode_kanca_raw
            
            all_preview_data.append({
                'kode_kanca': kode_kanca,
                'kode_uker': str(row[COLUMN_INDICES['kode_uker']]).strip(),
                'nama_kanca': str(row[COLUMN_INDICES['nama_kanca']]).strip(),
                'nama_uker': str(row[COLUMN_INDICES['nama_uker']]).strip(),
                # KUR RITEL - Use clean_numeric_value to handle NaN
                'kur_deb': clean_numeric_value(row[COLUMN_INDICES['kur_deb']]),
                'kur_os': clean_numeric_value(row[COLUMN_INDICES['kur_os']]),
                'kur_pl': clean_numeric_value(row[COLUMN_INDICES['kur_pl']]),
                'kur_npl': clean_numeric_value(row[COLUMN_INDICES['kur_npl']]),
                'kur_dpk': clean_numeric_value(row[COLUMN_INDICES['kur_dpk']]),
                # SMALL SD 5M
                'small_deb': clean_numeric_value(row[COLUMN_INDICES['small_deb']]),
                'small_os': clean_numeric_value(row[COLUMN_INDICES['small_os']]),
                'small_pl': clean_numeric_value(row[COLUMN_INDICES['small_pl']]),
                'small_npl': clean_numeric_value(row[COLUMN_INDICES['small_npl']]),
                'small_dpk': clean_numeric_value(row[COLUMN_INDICES['small_dpk']]),
                # KECIL NCC
                'kecil_ncc_deb': clean_numeric_value(row[COLUMN_INDICES['kecil_ncc_deb']]),
                'kecil_ncc_os': clean_numeric_value(row[COLUMN_INDICES['kecil_ncc_os']]),
                'kecil_ncc_pl': clean_numeric_value(row[COLUMN_INDICES['kecil_ncc_pl']]),
                'kecil_ncc_npl': clean_numeric_value(row[COLUMN_INDICES['kecil_ncc_npl']]),
                'kecil_ncc_dpk': clean_numeric_value(row[COLUMN_INDICES['kecil_ncc_dpk']]),
                # KECIL CC
                'kecil_cc_deb': clean_numeric_value(row[COLUMN_INDICES['kecil_cc_deb']]),
                'kecil_cc_os': clean_numeric_value(row[COLUMN_INDICES['kecil_cc_os']]),
                'kecil_cc_pl': clean_numeric_value(row[COLUMN_INDICES['kecil_cc_pl']]),
                'kecil_cc_npl': clean_numeric_value(row[COLUMN_INDICES['kecil_cc_npl']]),
                'kecil_cc_dpk': clean_numeric_value(row[COLUMN_INDICES['kecil_cc_dpk']]),
            })
        
        context = {
            'page_title': 'Preview Komitmen Upload',
            'filename': filename,
            'notes': notes,
            'periode': periode,
            'validation': validation_result,
            'compare': compare_result,
            'all_data': all_preview_data,  # ALL data untuk dicek
            'total_columns': 24,  # A-X
        }
        return render(request, 'data_management/preview_komitmen.html', context)
        
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('data_management:upload_komitmen')


@admin_required
def confirm_komitmen_upload(request):
    """Confirm and save komitmen data - Step 3: Final save"""
    from .validators import validate_komitmen_excel
    from .utils import save_komitmen_data
    from dashboard.models import KomitmenUpload
    from datetime import datetime
    import os
    
    if request.method != 'POST':
        return redirect('data_management:upload_komitmen')
    
    temp_file = request.session.get('komitmen_temp_file')
    filename = request.session.get('komitmen_filename')
    notes = request.session.get('komitmen_notes', '')
    periode_str = request.session.get('komitmen_periode')
    
    if not temp_file or not os.path.exists(temp_file):
        messages.error(request, 'Session expired. Silakan upload ulang.')
        return redirect('data_management:upload_komitmen')
    
    try:
        periode = datetime.fromisoformat(periode_str).date()
        
        # Re-validate one more time
        validation_result = validate_komitmen_excel(temp_file, periode)
        
        if not validation_result['valid']:
            messages.error(request, 'File tidak valid.')
            return redirect('data_management:upload_komitmen')
        
        # Create or update upload record
        upload_obj, created = KomitmenUpload.objects.update_or_create(
            periode=periode,
            defaults={
                'uploaded_by': request.user,
                'file_name': filename,
                'row_count': validation_result['data_row_count'],
                'status': 'processing',
                'notes': notes + '\n\n' + '\n'.join(validation_result['warnings'])
            }
        )
        
        # Save data
        saved_count = save_komitmen_data(
            validation_result['data_df'],
            periode,
            upload_obj
        )
        
        # Update status
        upload_obj.status = 'completed'
        upload_obj.row_count = saved_count
        upload_obj.save()
        
        # Cleanup temp file
        os.remove(temp_file)
        os.rmdir(os.path.dirname(temp_file))
        
        # Clear session
        del request.session['komitmen_temp_file']
        del request.session['komitmen_filename']
        del request.session['komitmen_notes']
        del request.session['komitmen_periode']
        
        action = 'diperbarui' if not created else 'berhasil diupload'
        messages.success(
            request,
            f'✅ Komitmen {periode.strftime("%B %Y")} {action}! '
            f'{saved_count} baris data tersimpan.'
        )
        
        return redirect('data_management:komitmen_history')
        
    except Exception as e:
        messages.error(request, f'Error saat menyimpan data: {str(e)}')
        return redirect('data_management:preview_komitmen')


@admin_required
def komitmen_history(request):
    """Show list of all komitmen uploads"""
    from dashboard.models import KomitmenUpload
    
    uploads = KomitmenUpload.objects.all().select_related('uploaded_by')
    
    # Pagination
    paginator = Paginator(uploads, 12)  # 12 months per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_title': 'History Komitmen',
        'uploads': page_obj,
        'total_uploads': uploads.count(),
    }
    return render(request, 'data_management/komitmen_history.html', context)


@admin_required
def delete_komitmen(request, upload_id):
    """Delete komitmen upload and all related data"""
    from dashboard.models import KomitmenUpload, KomitmenData
    
    try:
        upload = KomitmenUpload.objects.get(id=upload_id)
    except KomitmenUpload.DoesNotExist:
        messages.error(request, 'Data tidak ditemukan.')
        return redirect('data_management:komitmen_history')
    
    if request.method == 'POST':
        periode_display = upload.periode_display()
        data_count = KomitmenData.objects.filter(upload=upload).count()
        
        # Delete (cascade akan otomatis delete KomitmenData)
        upload.delete()
        
        messages.success(
            request,
            f'✅ Komitmen {periode_display} berhasil dihapus! '
            f'({data_count} baris data dihapus)'
        )
        return redirect('data_management:komitmen_history')
    
    # Show confirmation page
    data_count = KomitmenData.objects.filter(upload=upload).count()
    
    context = {
        'page_title': 'Hapus Komitmen',
        'upload': upload,
        'data_count': data_count,
    }
    return render(request, 'data_management/delete_komitmen.html', context)


@admin_required
def view_komitmen(request):
    """View all komitmen data with inline editing capability"""
    from dashboard.models import KomitmenUpload, KomitmenData
    
    # Get selected periode from query params
    selected_periode = request.GET.get('periode')
    
    # Get all available periodes
    uploads = KomitmenUpload.objects.all().order_by('-periode')
    
    # Default to latest periode if none selected
    if not selected_periode and uploads.exists():
        selected_periode = uploads.first().periode.strftime('%Y-%m-%d')
    
    # Get data for selected periode
    komitmen_data = []
    selected_upload = None
    
    if selected_periode:
        try:
            from datetime import datetime
            periode_date = datetime.strptime(selected_periode, '%Y-%m-%d').date()
            selected_upload = KomitmenUpload.objects.filter(periode=periode_date).first()
            
            if selected_upload:
                # Get all komitmen data for this periode, ordered by kode_uker
                data_queryset = KomitmenData.objects.filter(upload=selected_upload).order_by('kode_uker')
                
                for data in data_queryset:
                    komitmen_data.append({
                        'id': data.id,
                        'kode_kanca': data.kode_kanca,
                        'kode_uker': data.kode_uker,
                        'nama_kanca': data.nama_kanca,
                        'nama_uker': data.nama_uker,
                        # KUR RITEL
                        'kur_deb': data.kur_deb,
                        'kur_os': data.kur_os,
                        'kur_pl': data.kur_pl,
                        'kur_npl': data.kur_npl,
                        'kur_dpk': data.kur_dpk,
                        # SMALL SD 5M
                        'small_deb': data.small_deb,
                        'small_os': data.small_os,
                        'small_pl': data.small_pl,
                        'small_npl': data.small_npl,
                        'small_dpk': data.small_dpk,
                        # KECIL NCC
                        'kecil_ncc_deb': data.kecil_ncc_deb,
                        'kecil_ncc_os': data.kecil_ncc_os,
                        'kecil_ncc_pl': data.kecil_ncc_pl,
                        'kecil_ncc_npl': data.kecil_ncc_npl,
                        'kecil_ncc_dpk': data.kecil_ncc_dpk,
                        # KECIL CC
                        'kecil_cc_deb': data.kecil_cc_deb,
                        'kecil_cc_os': data.kecil_cc_os,
                        'kecil_cc_pl': data.kecil_cc_pl,
                        'kecil_cc_npl': data.kecil_cc_npl,
                        'kecil_cc_dpk': data.kecil_cc_dpk,
                    })
        except Exception as e:
            messages.error(request, f'Error loading data: {str(e)}')
    
    context = {
        'page_title': 'View Komitmen Data',
        'uploads': uploads,
        'selected_periode': selected_periode,
        'selected_upload': selected_upload,
        'komitmen_data': komitmen_data,
        'total_rows': len(komitmen_data),
    }
    return render(request, 'data_management/view_komitmen.html', context)


@admin_required
def update_komitmen_cell(request):
    """AJAX endpoint for updating single cell value"""
    from dashboard.models import KomitmenData
    from decimal import Decimal, InvalidOperation
    
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            row_id = data.get('row_id')
            field_name = data.get('field_name')
            new_value = data.get('value')
            
            # Get the komitmen data row
            komitmen_row = KomitmenData.objects.get(id=row_id)
            
            # Validate field name (prevent SQL injection)
            allowed_fields = [
                'kur_deb', 'kur_os', 'kur_pl', 'kur_npl', 'kur_dpk',
                'small_deb', 'small_os', 'small_pl', 'small_npl', 'small_dpk',
                'kecil_ncc_deb', 'kecil_ncc_os', 'kecil_ncc_pl', 'kecil_ncc_npl', 'kecil_ncc_dpk',
                'kecil_cc_deb', 'kecil_cc_os', 'kecil_cc_pl', 'kecil_cc_npl', 'kecil_cc_dpk',
            ]
            
            if field_name not in allowed_fields:
                return JsonResponse({
                    'success': False,
                    'error': 'Field tidak valid'
                }, status=400)
            
            # Convert value to Decimal
            try:
                if new_value == '' or new_value is None or new_value == '-':
                    decimal_value = None
                else:
                    # Remove formatting (commas, spaces)
                    clean_value = str(new_value).replace(',', '').replace(' ', '').strip()
                    decimal_value = Decimal(clean_value) if clean_value else None
            except (InvalidOperation, ValueError):
                return JsonResponse({
                    'success': False,
                    'error': 'Format angka tidak valid'
                }, status=400)
            
            # Update the field
            old_value = getattr(komitmen_row, field_name)
            setattr(komitmen_row, field_name, decimal_value)
            komitmen_row.save()
            
            # Format for display
            if decimal_value is None:
                display_value = '-'
            elif field_name.endswith('_pl') or field_name.endswith('_npl'):
                display_value = f"{decimal_value:.2f}"
            else:
                display_value = f"{decimal_value:,.0f}"
            
            return JsonResponse({
                'success': True,
                'display_value': display_value,
                'old_value': str(old_value) if old_value else '-',
                'new_value': str(decimal_value) if decimal_value else '-'
            })
            
        except KomitmenData.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Data tidak ditemukan'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Method not allowed'
    }, status=405)
