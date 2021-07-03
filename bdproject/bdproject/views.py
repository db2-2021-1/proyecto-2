from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .invertedindex.index import inverse_index
import os.path
import glob
from pathlib import Path
import json
from django.http import JsonResponse, StreamingHttpResponse

index = inverse_index()
if not os.path.isfile("index"):
  index.from_json(glob.glob("../data_elecciones/*.json"))
  index.dump()
else:
  index.load()

def mainpage(request):
  return render(request,'index.html')

def dashboard(request):
  return render(request, 'dashboard.html')

@csrf_exempt
def invertedindexquery(request):
  #valor = request['input']
  #received_json_data = json.loads(request.POST['query'])
  retorno = ['1046566853970153472', '1046566883145797633', '1046567317847646208', '1046567761265262594', '1046568327458566144']
  
  print(json.dumps(retorno))

  return JsonResponse(json.dumps(retorno) , safe=False)