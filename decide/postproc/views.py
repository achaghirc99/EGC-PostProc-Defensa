from rest_framework.views import APIView
from rest_framework.response import Response
import math
from pickle import TRUE, FALSE
from optparse import Option
import random


class PostProcView(APIView):

    def identity(self, options):
        out = []

        for opt in options:
            out.append({
                **opt,
                'postproc': opt['votes'],
            })

        out.sort(key=lambda x: -x['postproc'])
        return Response(out)
      
    def simple(self, options, escanio):
        out = []
        for simp in options:
            out.append({
                **simp,
                'postproc': 0,
            })
        out.sort(key=lambda x: -x['votes'])

        sea = escanio
        n = 0

        for votes in out:
                n = votes['votes'] + n
        
        valEs = n/sea

        n1 = 0
        while sea > 0:
            if n1 < len(out):
                escanio_ = math.trunc(out[n1]['votes']/valEs) 
                out[n1]['postproc'] = escanio_
                sea = sea - escanio_
                n1 = n1+1
            else:
                now = 0
                c = 1
                while c <len(out):
                    vAct = out[now]['votes']/valEs - out[now]['postproc']
                    vCom = out[c]['votes']/valEs - out[c]['postproc']
                    if(vAct >= vCom):
                        c = c + 1
                    else:
                        now=c
                        c = c + 1
                out[now]['postproc'] = out[now]['postproc'] + 1
                sea = sea - 1
        return out

    #Sistema D'Hondt - Metodo de promedio mayor para asignar escaños en sistemas de representación proporcional por listas electorales. Por tanto,
    # en dicho método trabajaremos con listas de partidos politicos y con un número de escaños que será pasado como parámetro. 
    #           Fórmula de D'Hondt: cociente = V/S+1    , siendo V: el número total de votosS
    #                                                            S: el num. de escaños que posee en el momento
    def dhondt(self, options, totalEscanio,cands):

        #Salida
        out = [] 

        #Añadimos a options un parámetro llamado 'escanio' que será donde
        #guardaremos la cantidad de escaños por opción y nuestra 'S' en la fórmula de D'Hondt
        for opt in options:
            out.append({
                **opt, 

                'escanio': 0,
            })

        #Igualamos numEscanos al numero total de escaños a repartir
        numEscanos = totalEscanio

        #Mientras no se repartan todos los escaños hacemos lo siguiente
        while numEscanos>0:
            
            actual = 0
            
            #Comparamos todas las opciones posibles
            for i in range(1, len(out)):
                valorActual = out[actual]['votes'] / (out[actual]['escanio'] + 1)
                valorComparar = out[i]['votes'] / (out[i]['escanio'] + 1)

                #Si el valor a comparar es mayor que el valor actual mayor se cambian
                if(valorActual<valorComparar):
                    actual = i
            
            #Al final de recorrer todos, la opcion cuyo indice es actual es el que posee más votos y,
            #por tanto, se le añade un escaño
            out[actual]['escanio'] = out[actual]['escanio'] + 1
            numEscanos = numEscanos - 1
        
        #Ordenamos las diferentes opciones por su número total de escaños obtenidos durante el método
        out.sort(key = lambda x: -x['escanio'])
        
        #En el caso de que la lista de candidatos no este vacía, se realiza la paridad.
        if (cands != []):
            out = self.paridad(out, cands)
        
        return Response(out)

    def mgu(self, options,Totalseats):
        out = []

        for o in options:

            out.append({
                **o,
                'escanio': 0,
            })
        
        out.sort(key=lambda x: -x['votes'])

        mv = out[0]['votes']
        ng=0

        for element in out:
            if element['votes']== mv:
                ng =ng + 1
            
        if ng == 1:
            out[0]['escanio'] = Totalseats
        else:
            r = Totalseats % ng
            c = Totalseats// ng
            if r== 0:
                a=0
                for x in range(0,ng):
                   out[x]['escanio'] = c
            else:
                if ng == len(out) and ng < Totalseats:
                    out[0]['escanio'] = c + r
                    for x in range(1,ng):
                        out[x]['escanio'] = c
                else:
                    if ng > Totalseats:
                        for x in range(0,r):
                          out[x]['escanio'] = 1
                    else:
                        for x in range(0,ng):
                            out[x]['escanio'] =c
                        out[ng]['escanio'] =r
        return out
    
    def comprobar(self,opts,cands):
        comprueba = False   
        out = []
        for opt in opts:
            out.append({
                **opt
            })
        for i in out:
            mujeres =[]
            hombres=[]
            for c in cands:
                if c['sex'] == 'M':
                    mujeres.append(c)
                elif c['sex'] == 'H':
                    hombres.append(c)
            comprueba= self.porcentaje_genero(hombres,mujeres)
            if ~comprueba:
                break
        return comprueba
    
    def comprobar_edad(self, opts, cands):
        comprueba = False   
        out = []
        for opt in opts:
            out.append({
                **opt
            })

        menoresDe30 =[]
        mayoresDe30=[]
        for c in cands:
            if c['age'] <=30:
                menoresDe30.append(c)
            elif c['age'] > 30:
                mayoresDe30.append(c)
        comprueba= self.porcentaje_edad(menoresDe30,mayoresDe30)
        return comprueba
    
    def porcentaje_edad(self, menoresDe30, mayoresDe30):
        suma = len(menoresDe30) + len(mayoresDe30)
        porcentaje_menoresDe30 = len(menoresDe30)/suma
        porcentaje_mayoresDe30 = len(mayoresDe30)/suma
        if(porcentaje_menoresDe30 < porcentaje_mayoresDe30):
            return "La mayoria de candidatos son mayores de 30 años."
        elif (porcentaje_menoresDe30 > porcentaje_mayoresDe30): 
            return "La mayoria de candidatos son menores de 30 años."
        else:
            return "Hay los mismo candidatos mayores como menores de 30."
        
    def porcentaje_genero(self, mujeres, hombres):
        suma = len(mujeres) + len(hombres)
        porcentaje_mujeres = len(mujeres)/suma
        porcentaje_hombres = len(hombres)/suma
        if(porcentaje_mujeres< 0.4) or (porcentaje_hombres <0.4):
            return False    
        else:
            return True
    
    def paridad (self,options,cands):
        out = []

        for opt in options:
            out.append({
                **opt,
                'paridad': [],
                })
        
        hombres = []
        mujeres = []
        for cand in cands:
            if cand['sex'] == 'H':
                hombres.append(cand)
            elif cand['sex'] == 'M':
                mujeres.append(cand)
        
        for indice in out:
            escanios = indice['escanio']
            hom = 0
            muj = 0
            paridad = True
            while escanios > 0:
                if paridad: 
                    if muj < len(mujeres):
                        indice['paridad'].append(mujeres[muj])
                        muj = muj + 1
                        escanios -=1
                    paridad = False
                else: 
                    if hom < len(hombres):
                        indice['paridad'].append(hombres[hom])
                        hom = hom + 1
                        escanios -=1
                    paridad = True
                if(muj == len(mujeres) and hom == len(hombres)):
                    escanios = 0
                    break
        return out
      
    def saintelague(self, options, escanio,cands):
        
        #Definimos las variables

        partidos = [] 
        puntosPorPart = [] 
        escanos = [] 
        out = [] 

       #Ponemos los escaños iniciales de todos los partidos a 0
        for n in options:
            escanosIniciales = 0
            escanos.append(escanosIniciales)

        #Añadimos los votos a cada partido y a out todas las salidas anterioes mas los escaños
        for opt in options:
            partidos.append(opt['votes']) 
            out.append({
                **opt,
                'escanio': 0,
                })

        #Inicializamos la lista así para que no se cambie por referencia
        puntosPorPart = partidos[:]
        escanosTotales = escanio 
        #Dividimos entre 1.4 el primer valor de votos de cada partido para hacer el sainte lague modificado
        for p in puntosPorPart:
            index1=puntosPorPart.index(p)
            puntosPorPart[index1]=p/1.4
        
        #Realizamos la iteracion tantas veces como escaños a repartir haya
        i = 0
        while(i<escanosTotales):
        #Sacamos el partido con más votos ahora mismo
            maxVotos = max(puntosPorPart) 
        #Lo localizamos en index
            index = puntosPorPart.index(maxVotos)
        #Si es distinto a 0 le aplicamos sante lague a ese partido y recalculamos sus votos
            if maxVotos != 0:
                
                escanos[index] += 1 
                out[index]['escanio'] += 1 
                puntosPorPart[index] = partidos[index] / ((2*escanos[index])+1) 

            i=i+1
            
        out.sort(key=lambda x: -x['escanio'])
        if (cands != []):
            out = self.paridad(out, cands)
        return Response(out)
    
    def post(self, request):
        """
         * type: IDENTITY | EQUALITY | WEIGHT | MGU
         * options: [
            {
             option: str,
             number: int,
             votes: int,
             ...extraparams
            }
           ]
        """

        t = request.data.get('type')
        opts = request.data.get('options', [])
        cands = request.data.get('candidates', [])
        s = request.data.get('escanio')

        if t == 'IDENTITY':
            return self.identity(opts)
        elif t == 'DHONDT':
            return self.dhondt(opts, request.data.get('escanio'),cands)
        elif t == 'SIMPLE':
            return Response(self.simple(opts,s))
        elif t == 'SIMPLEP':
            mensaje = self.comprobar_edad(opts,cands)
            res = self.simple(opts,s)
            return Response({'mensaje':mensaje, 'res':res})
        elif t == 'MGU':
            return Response(self.mgu(opts,s))
        elif t == 'MGUCP':
            comprueba= self.comprobar(opts,cands)
            if comprueba:
                options= []
                options = self.mgu(opts,s)
                return Response(self.paridad(options,cands))
            else:
                return Response({'message' : 'la diferencia del numero de hombres y mujeres es de más de un 60% - 40%'})        
        elif t == 'SAINTELAGUE':
            return self.saintelague(opts,s,cands)
        elif t == 'SAINTELAGUETCP':
            return self.saintelague(opts,s,cands)
        elif t == 'PARIDAD':
            comprueba= self.comprobar(opts,cands)
            if comprueba:
                return Response(self.paridad(opts,cands))
            else:
                return Response({'message' : 'la diferencia del numero de hombres y mujeres es de más de un 60% - 40%'})        
        return Response({})
