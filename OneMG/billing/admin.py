from django.contrib import admin
from billing.models import BillMapping
from django.http import HttpResponse
from datetime  import datetime


def export_xls(modeladmin, request, queryset):
    import xlwt
    fileName = datetime.now().strftime("%d_%B_%Y_%I_%M_%s")
    response = HttpResponse()
    response['Content-Disposition'] = 'attachment; filename=' + fileName + '.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    fileName=datetime.now().strftime("%d_%B_%Y_%I_%M_%s")
    ws = wb.add_sheet(fileName)

    row_num = 0
    columns = [
        (u"medicokare_inv_no", 5000),
        (u"medicokare_amount", 6000),
        (u"settled_amount", 8000),
        (u"is_settled", 1000),
        (u"discount_to_business", 5000),
    ]

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    for col_num in xrange(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], font_style)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    font_style = xlwt.XFStyle()
    font_style.alignment.wrap = 1

    for obj in queryset:
        row_num += 1
        row = [
            obj.medicokare_inv_no,
            obj.medicokare_amount,
            obj.settled_amount,
            obj.is_settled,
            obj.discount_to_business,
        ]
        for col_num in xrange(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


export_xls.short_description = u"Export XLS"



class ModelBillMappingAdmin(admin.ModelAdmin):
    list_display=['medicokare_inv_no','medicokare_amount','settled_amount','is_settled','discount_to_business']
    list_filter = ['is_settled']
    search_fields = ('medicokare_inv_no',)
    actions = [export_xls, ]

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(ModelBillMappingAdmin, self).get_search_results(request, queryset, search_term)
        try:
            search_term_as_int = int(search_term)
            queryset |= self.model.objects.filter(medicokare_inv_no__icontains=search_term_as_int)
        except:
            pass
        return queryset, use_distinct



admin.site.register(BillMapping,ModelBillMappingAdmin)