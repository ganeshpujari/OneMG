from django.db import models
from django.contrib import admin
import xlrd
from dateutil import parser
from OneMG.settings import BASE_DIR




class FailureLog(models.Model):
    source=models.CharField(max_length=250)
    inv_no = models.BigIntegerField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

admin.site.register(FailureLog)


def failure_entry(source,inv_no):
    fLogObj=FailureLog()
    fLogObj.source=source
    fLogObj.inv_no=inv_no
    fLogObj.save()



class BillMapping(models.Model):
    medicokare_inv_no=models.BigIntegerField(unique=True)
    medicokare_inv_date=models.DateField(null=True,blank=True)
    medicokare_party=models.CharField(max_length=250,null=True,blank=True)
    medicokare_amount=models.FloatField()
    is_settled=models.BooleanField(default=False)
    settled_amount=models.FloatField(null=True,blank=True)
    settled_date=models.DateField(null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    raw_seted_date=models.CharField(max_length=250,null=True,blank=True)
    discount_to_business=models.FloatField(null=True,blank=True)


# admin.site.register(BillMapping)


def add_medicokare_data(medicokare_inv_no,medicokare_inv_date,medicokare_party,medicokare_amount):
    if not BillMapping.objects.filter(medicokare_inv_no=medicokare_inv_no).exists():
        billMapObj=BillMapping()
        billMapObj.medicokare_inv_no =medicokare_inv_no
        billMapObj.medicokare_inv_date =medicokare_inv_date
        billMapObj.medicokare_party =medicokare_party
        billMapObj.medicokare_amount =medicokare_amount
        billMapObj.save()
    else:
        failure_entry('Medicokare', medicokare_inv_no)

def update_one_mg_data(one_mg_inv_no,is_settled,settled_amount,settled_date):
    try:
        billMapObj=BillMapping.objects.get(medicokare_inv_no=one_mg_inv_no)
        billMapObj.is_settled=is_settled
        billMapObj.settled_amount=settled_amount
        try:
            settled_date=parser.parse(settled_date)
        except:
            billMapObj.raw_seted_date=settled_date
            settled_date=None
        billMapObj.settled_date=settled_date
        if is_settled:
            discount_to_business=100-((billMapObj.settled_amount/billMapObj.medicokare_amount)*100)
            billMapObj.discount_to_business=discount_to_business
        billMapObj.save()

    except BillMapping.DoesNotExist,e:
        failure_entry('OneMG', one_mg_inv_no)



class Uploads(models.Model):
    medicokare=models.FileField(upload_to=BASE_DIR+'/media',blank=True,null=True)
    oneMg=models.FileField(upload_to=BASE_DIR+'/media',blank=True,null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        super(Uploads, self).save(*args, **kwargs)
        FailureLog.objects.all().delete()
        medicokareFilePath=self.medicokare.path if self.medicokare else None
        oneMgFilePath=self.oneMg.path if self.oneMg else None
        if medicokareFilePath:
            medicokareWorkbook = xlrd.open_workbook(medicokareFilePath)
            sh = medicokareWorkbook.sheet_by_index(0)

            for n in range(sh.nrows):
                try:
                    if n > 1:
                        medicokare_inv_no=str(sh.cell_value(n, 0)).upper().replace("MK","").replace("-","").replace(" ","")
                        if len(medicokare_inv_no)<=0:
                            break
                        medicokare_inv_date_raw=str(sh.cell_value(n, 1))
                        try:
                            medicokare_inv_date=parser.parse(medicokare_inv_date_raw)
                        except:
                            medicokare_inv_date=None
                        medicokare_party=str(sh.cell_value(n, 2))
                        medicokare_amount=sh.cell_value(n, 3)
                        add_medicokare_data(int(medicokare_inv_no),medicokare_inv_date,medicokare_party,medicokare_amount)
                except Exception,e:
                    print (e)

        if oneMgFilePath:
            oneMgWorkbook = xlrd.open_workbook(oneMgFilePath)
            mgsh = oneMgWorkbook.sheet_by_index(0)
            n = 1
            i = 0
            for n in range(mgsh.nrows):
                try:
                    if n != 0:
                        one_mg_inv_no = str(mgsh.cell_value(n, 5)).upper().replace("MK", "").replace("-", "").replace(" ", "")
                        settled=str(mgsh.cell_value(n, 14)).lower()
                        is_settled = True if settled=="settled" else False
                        amount_settledRaw=str((mgsh.cell_value(n, 15)))
                        settled_amount=float(amount_settledRaw) if len(amount_settledRaw)>0 else 0
                        settled_date=str((mgsh.cell_value(n, 16)))
                        update_one_mg_data(int(one_mg_inv_no),is_settled,settled_amount,settled_date)
                except Exception, e:
                    raise (e)






admin.site.register(Uploads)