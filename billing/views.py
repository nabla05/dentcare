from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Payslip
from clinic.models import Employee
from clinic.utils import staff_required
from decimal import Decimal


# ── Payslip List ───────────────────────────────────────
@staff_required
def payslip_list(request):
    payslips = Payslip.objects.select_related('employee__user').all()

    filter_status = request.GET.get('status', '')
    filter_year   = request.GET.get('year', '')

    if filter_status:
        payslips = payslips.filter(status=filter_status)
    if filter_year:
        payslips = payslips.filter(year=filter_year)

    paginator   = Paginator(payslips, 10)
    page_number = request.GET.get('page')
    page_obj    = paginator.get_page(page_number)

    years = Payslip.objects.values_list('year', flat=True).distinct().order_by('-year')

    return render(request, 'billing/payslips/list.html', {
        'page_obj':      page_obj,
        'filter_status': filter_status,
        'filter_year':   filter_year,
        'years':         years,
        'total':         payslips.count(),
        'statuses':      Payslip.Status.choices,
    })


# ── Add Payslip ────────────────────────────────────────
@staff_required
def payslip_add(request):
    employees = Employee.objects.filter(status='active').select_related('user')

    if request.method == 'POST':
        try:
            employee = get_object_or_404(Employee, pk=request.POST['employee'])
            Payslip.objects.create(
                employee    = employee,
                month       = request.POST['month'],
                year        = request.POST['year'],
                base_salary = Decimal(request.POST['base_salary']),
                bonuses     = Decimal(request.POST.get('bonuses', 0)),
                deductions  = Decimal(request.POST.get('deductions', 0)),
                status      = request.POST.get('status', 'pending'),
                notes       = request.POST.get('notes', ''),
            )
            messages.success(request, 'Payslip created successfully!')
            return redirect('billing:payslip_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')

    return render(request, 'billing/payslips/form.html', {
        'action':    'Add',
        'employees': employees,
        'months':    Payslip.Month.choices,
        'statuses':  Payslip.Status.choices,
    })


# ── Edit Payslip ───────────────────────────────────────
@staff_required
def payslip_edit(request, pk):
    payslip   = get_object_or_404(Payslip, pk=pk)
    employees = Employee.objects.filter(status='active').select_related('user')

    if request.method == 'POST':
        try:
            payslip.employee    = get_object_or_404(Employee, pk=request.POST['employee'])
            payslip.month       = request.POST['month']
            payslip.year        = request.POST['year']
            payslip.base_salary = Decimal(request.POST['base_salary'])
            payslip.bonuses     = Decimal(request.POST.get('bonuses', 0))
            payslip.deductions  = Decimal(request.POST.get('deductions', 0))
            payslip.status      = request.POST.get('status', 'pending')
            payslip.notes       = request.POST.get('notes', '')
            payslip.save()
            messages.success(request, 'Payslip updated successfully!')
            return redirect('billing:payslip_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')

    return render(request, 'billing/payslips/form.html', {
        'action':    'Edit',
        'payslip':   payslip,
        'employees': employees,
        'months':    Payslip.Month.choices,
        'statuses':  Payslip.Status.choices,
    })


# ── Delete Payslip ─────────────────────────────────────
@staff_required
def payslip_delete(request, pk):
    payslip = get_object_or_404(Payslip, pk=pk)
    if request.method == 'POST':
        payslip.delete()
        messages.success(request, 'Payslip deleted.')
        return redirect('billing:payslip_list')
    return render(request, 'billing/payslips/confirm_delete.html', {
        'payslip': payslip
    })


# ── Generate PDF ───────────────────────────────────────
@staff_required
def payslip_pdf(request, pk):
    payslip  = get_object_or_404(Payslip, pk=pk)
    template = get_template('billing/payslips/pdf_template.html')
    html     = template.render({'payslip': payslip})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="payslip_{payslip.employee.emp_id}'
        f'_{payslip.month}_{payslip.year}.pdf"'
    )

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('PDF generation error', status=500)
    return response