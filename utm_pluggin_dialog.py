# -*- coding: utf-8 -*-
"""
/***************************************************************************
 UTMDialog
                                 A QGIS plugin
 este plugin hace la conversion de coordenadas geografica a coordenadas planas UTM
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-04-16
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Carlos Archaga 
        email                : caarchaga@unah.hn
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import math

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'utm_pluggin_dialog_base.ui'))


class UTMDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(UTMDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.LatD.valueChanged.connect(self.cambio) 
        self.LonD.valueChanged.connect(self.cambio) 
        self.zonaUTM.valueChanged.connect(self.cambio) 
        self.BanZone.currentTextChanged.connect(self.cambio)  #tipo de banda que definiremos para la proyeccion
        self.cmbMer.valueChanged.connect(self.cambio) 
    def cambio(self):
        #covertir los valores de grados decimales a radianes
        float_latitud = self.LatD.value()
        float_longitud = self.LonD.value() 
        int_zona = self.zonaUTM.value() 
        str_banda = self.BanZone.currentText() 
        float_coorx = self.UTM_X.value() 
        float_coory = self.UTM_Y.value() 
        int_meridiano = self.cmbMer.value()  
        #variables que calculan exentricidad de los meridianos para el calculo de las coordenadas geograficas a coordenas proyectadas
        # #Factor de Escala
        K0 = 0.9996 #variable constante 
        #Excentricidades
        E = 0.00669438 #variable constante 
        E2 = E * E #exentricidad elevado por si mismo
        E3 = E2 * E #exentricidad eleavda al cubo por si mismo
        E_P2 = E / (1 - E) #exentricidad p2 
        #Segundas Excentricidades
        SQRT_E = math.sqrt(1 - E)
        _E = (1 - SQRT_E) / (1 + SQRT_E)
        _E2 = _E * _E
        _E3 = _E2 * _E
        _E4 = _E3 * _E
        _E5 = _E4 * _E
        
        #Ecuaciones de la conversion a UTM
        M1 = (1 - E / 4 - 3 * E2 / 64 - 5 * E3 / 256) #primera formula 
        M2 = (3 * E / 8 + 3 * E2 / 32 + 45 * E3 / 1024) #segunda formula 
        M3 = (15 * E2 / 256 + 45 * E3 / 1024) #tercera formula 
        M4 = (35 * E3 / 3072)  #cuarta formula 
        #Ecuaciones de la conversion a Lat Lon
        P2 = (3 / 2 * _E - 27 / 32 * _E3 + 269 / 512 * _E5)
        P3 = (21 / 16 * _E2 - 55 / 32 * _E4)
        P4 = (151 / 96 * _E3 - 417 / 128 * _E5)
        P5 = (1097 / 512 * _E4)
        #Semieje del Elipsoide (WGS84)
        R = 6378137 #variable que define el semieje del elipsoide 
        #Bandas UTM
        ZONE_LETTERS = "CDEFGHJKLMNPQRSTUVWXX" #letras que representan cada zona 
        NORTH_LETTERS = "NPQRSTUVWXX" #letras asignadas para la zona norte 
        SOUTH_LETTERS = "CDEFGHJKLM"  #ketras asignadas para la zona sur  
        #variables que obtienen los parmetors de los widgthes de la interfaz grafica
        phi = float_latitud
        phiRad = math.radians(phi)
        lamb = float_longitud
        lambRad = math.radians(lamb)
        #calcular la zona de referencia del meridiano de referencia utm 
        #Huso
        huso = int((lamb/6) + 31)
        self.zonaUTM.setValue(huso) #el valor del meridiano central tomara el valor del splint box con el metodo setvalue 
        #Meridiano central de la zona
        #variable que define el meridiano central de proyeccion 
        cenMer = 6 * (huso - 1) - 177
        self.cmbMer.setValue(cenMer)
        cenMer_rad = math.radians(cenMer)
        #Letra de Zona
        #funcion para definir la banda del meridiano de referncia wgs84 UTM
        if -80 <= phi <= 84:
            zona = ZONE_LETTERS[int(phi + 80) >> 3]
            zona_str = str(zona)
        self.BanZone.setCurrentText(zona) 
        #calcular coordenadas  
        #determinar seno , coseno y tangente de los valores radianes de la latitud  
        cosRad= math.cos(phiRad)
        tanRad = math.tan(phiRad)
        sinRad = math.sin(phiRad)
        tanRad2 = tanRad**2
        tanRad4 = tanRad2**2
        #Calcula el valor de N 
        #Calcula el valor de N tomando de parametros el R Semieje del Elipsoide (WGS84)
        n = R / math.sqrt(1 - E * sinRad**2)
        #calcular el valor de C 
        c = E_P2 * cosRad**2
        #Ecuaciones de la proyecci??n
        a = cosRad * (((lambRad - cenMer_rad) + math.pi) % (2 * math.pi) - math.pi)
        a2 = a * a
        a3 = a2 * a
        a4 = a3 * a
        a5 = a4 * a
        a6 = a5 * a
        m = R * (M1 * phiRad -
             M2 * math.sin(2 * phiRad) +
             M3 * math.sin(4 * phiRad) -
             M4 * math.sin(6 * phiRad)) 
        #calculo de coodenadas x proyectadas ecuacion de trasnformacion 
        X = K0 * n * (a +
                  a3 / 6 * (1 - tanRad2 + c) +
                  a5 / 120 * (5 - 18 * tanRad2 + tanRad4 + 72 * c - 58 * E_P2)) + 500000
        #calculo de coordenada y proyectada ecuacion de trasnformacion 
        y = K0 * (m + n * tanRad * (a2 / 2 +
              a4 / 24 * (5 - tanRad2 + 9 * c + 4 * c**2) +
              a6 / 720 * (61 - 58 * tanRad2 + tanRad4 + 600 * c - 330 * E_P2))) 
        if phi >= 0:
            Y = y
        else:
            Y = 10000000 + y
        self.UTM_X.setValue(X) 
        self.UTM_Y.setValue(Y) 



    

    
    


    



     
     





