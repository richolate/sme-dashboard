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
    from .validators import validate_komitmen_excel
    from .utils import compare_komitmen_data
    from datetime import datetime
    import os
    
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
            all_preview_data.append({
                'kode_kanca': str(row[COLUMN_INDICES['kode_kanca']]).strip(),
                'kode_uker': str(row[COLUMN_INDICES['kode_uker']]).strip(),
                'nama_kanca': str(row[COLUMN_INDICES['nama_kanca']]).strip(),
                'nama_uker': str(row[COLUMN_INDICES['nama_uker']]).strip(),
                # KUR RITEL
                'kur_deb': row[COLUMN_INDICES['kur_deb']],
                'kur_os': row[COLUMN_INDICES['kur_os']],
                'kur_pl': row[COLUMN_INDICES['kur_pl']],
                'kur_npl': row[COLUMN_INDICES['kur_npl']],
                'kur_dpk': row[COLUMN_INDICES['kur_dpk']],
                # SMALL SD 5M
                'small_deb': row[COLUMN_INDICES['small_deb']],
                'small_os': row[COLUMN_INDICES['small_os']],
                'small_pl': row[COLUMN_INDICES['small_pl']],
                'small_npl': row[COLUMN_INDICES['small_npl']],
                'small_dpk': row[COLUMN_INDICES['small_dpk']],
                # KECIL NCC
                'kecil_ncc_deb': row[COLUMN_INDICES['kecil_ncc_deb']],
                'kecil_ncc_os': row[COLUMN_INDICES['kecil_ncc_os']],
                'kecil_ncc_pl': row[COLUMN_INDICES['kecil_ncc_pl']],
                'kecil_ncc_npl': row[COLUMN_INDICES['kecil_ncc_npl']],
                'kecil_ncc_dpk': row[COLUMN_INDICES['kecil_ncc_dpk']],
                # KECIL CC
                'kecil_cc_deb': row[COLUMN_INDICES['kecil_cc_deb']],
                'kecil_cc_os': row[COLUMN_INDICES['kecil_cc_os']],
                'kecil_cc_pl': row[COLUMN_INDICES['kecil_cc_pl']],
                'kecil_cc_npl': row[COLUMN_INDICES['kecil_cc_npl']],
                'kecil_cc_dpk': row[COLUMN_INDICES['kecil_cc_dpk']],
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
