from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from .models import UploadHistory
from .forms import UploadDataForm
from .utils import process_uploaded_file
from dashboard.models import LoanData


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
def upload_data_view(request):
    """
    View untuk upload data (hanya admin)
    """
    if request.method == 'POST':
        form = UploadDataForm(request.POST, request.FILES)
        if form.is_valid():
            upload_file = request.FILES['file']
            
            # Simpan upload history
            upload_history = UploadHistory.objects.create(
                uploaded_by=request.user,
                file_name=upload_file.name,
                file_path=upload_file,
                file_size=upload_file.size,
                status='pending',
                notes=form.cleaned_data.get('notes', ''),
            )
            
            # Process file (akan diimplementasi di utils.py)
            try:
                result = process_uploaded_file(upload_history)
                
                if result['success']:
                    upload_history.status = 'completed'
                    upload_history.total_rows = result['total_rows']
                    upload_history.successful_rows = result['successful_rows']
                    upload_history.failed_rows = result['failed_rows']
                    upload_history.completed_at = timezone.now()
                    if result.get('errors'):
                        upload_history.error_log = '\n'.join(result['errors'])
                    upload_history.save()
                    
                    messages.success(request, f'File berhasil diupload! Total: {result["total_rows"]}, Sukses: {result["successful_rows"]}, Gagal: {result["failed_rows"]}')
                else:
                    upload_history.status = 'failed'
                    upload_history.error_log = result['error']
                    upload_history.save()
                    
                    messages.error(request, f'Upload gagal: {result["error"]}')
            except Exception as e:
                upload_history.status = 'failed'
                upload_history.error_log = str(e)
                upload_history.save()
                
                messages.error(request, f'Terjadi kesalahan: {str(e)}')
            
            return redirect('data_management:upload_data')
    else:
        form = UploadDataForm()
    
    context = {
        'form': form,
        'page_title': 'Upload Data',
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
        # Implementasi delete data
        # Bisa berdasarkan tanggal, ID, atau kriteria lain
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        
        # TODO: Implementasi logic delete
        messages.success(request, 'Data berhasil dihapus.')
        return redirect('data_management:delete_data')
    
    context = {
        'page_title': 'Delete Data',
    }
    return render(request, 'data_management/delete_data.html', context)


@admin_required
def view_all_data_view(request):
    """Display an overview of LW321 for administrators."""

    loans = LoanData.objects.all().order_by('-periode', 'kanca', 'nomor_rekening')[:100]
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
