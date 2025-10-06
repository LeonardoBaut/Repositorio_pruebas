from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import xarray as xr
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.colors as mcolors
import os
import time
import earthaccess
import requests
import concurrent.futures

import pandas as pd
import dask
from dask.diagnostics import ProgressBar
from datetime import date
from fastapi.staticfiles import StaticFiles


# Autenticación inicial de Earthdata
auth = earthaccess.login(strategy="netrc")
print("Autenticación exitosa:", auth)

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8280"],  # Apache
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def download_granule(url, max_retries=3, retry_delay=5):
    print("Opening " + url)
    
    data_url = f'{url}.dap.nc4'

    # Specify variables for subsetting
    required_variables = {'T2M','PS','U10M','lon', 'lat', 'time'}

    basename = os.path.basename(data_url)
    save_path = os.path.join("datos_merra_2", basename)


    # Skip if file already downloaded
    if os.path.exists(save_path):
        print(f"File already exists, skipping: {save_path}")
        return

    request_params = {'dap4.ce': ';'.join(required_variables)}
    
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(data_url, params=request_params, headers={'Accept-Encoding': 'identity'}, timeout=30)
            if response.ok:
                with open(save_path, 'wb') as file_handler:
                    file_handler.write(response.content)
                print(f"Downloaded successfully: {save_path}")
                return
            else:
                print(f"Request failed (attempt {attempt}): {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Download error on attempt {attempt} for {save_path}: {e}")
        
        if attempt < max_retries:
            time.sleep(retry_delay)

    print(f"Failed to download after {max_retries} attempts: {save_path}")



###########################################################################################################

def graficar_temperatura_media(cloud_data_ds, variable='T2M', 
                               titulo="M2T1NXSLV.5.12.4 Mean Temperature and Freezing Line (°C) for October 2025",
                               nombre_salida="temperature_october_2025.png",
                               vmin=None, vmax=None,
                               region_xlim=(-90, -40), region_ylim=(-90, 90)):
    
    # Calcular promedio mensual (primer mes del dataset)
    temp_mean = cloud_data_ds[variable].resample(time='ME').mean()[0, :, :]

    plt.rcParams["figure.figsize"] = (14, 6.5)
    ax = plt.subplot(projection=ccrs.PlateCarree())

    # Normalización centrada en 0
    norm = mcolors.TwoSlopeNorm(
        vmin=vmin if vmin is not None else temp_mean.min().values,
        vcenter=0,
        vmax=vmax if vmax is not None else temp_mean.max().values
    )

    # Mapa de colores
    pm = ax.pcolormesh(temp_mean["lon"], temp_mean["lat"], temp_mean,
                       cmap='bwr', transform=ccrs.PlateCarree(), norm=norm)

    # Contorno línea de 0°C
    plt.contour(temp_mean['lon'], temp_mean['lat'], temp_mean,
                levels=[0], colors='purple', transform=ccrs.PlateCarree())

    # Elementos del mapa
    ax.coastlines()
    ax.gridlines(draw_labels=True)
    ax.add_feature(cfeature.STATES)

    # Límites de la región
    ax.set_xlim(region_xlim)
    ax.set_ylim(region_ylim)

    # Línea de congelación en leyenda
    freeze_line = mlines.Line2D([], [], color='purple', label='0°C Mean Freeze Line')
    plt.legend(handles=[freeze_line], loc='upper left')

    # Barra de color
    cbar = plt.colorbar(pm, ax=ax)
    cbar.set_label('Mean Temperature (°C)')

    # Título
    plt.suptitle(titulo, fontsize=11.5)

    plt.tight_layout(rect=[0, 0.05, 1, 0.95])

    # Guardar gráfico
    plt.savefig("./imagenes/"+nombre_salida, dpi=300)
    print(f"✅ Gráfico guardado en {nombre_salida}")
    plt.show()
    plt.close()

def graficar_presion_media(cloud_data_ds, variable='PS',
                           titulo="M2T1NXSLV.5.12.4 Mean Surface Pressure for October 2025",
                           nombre_salida="presion_october_2025.png",
                           vmin=None, vmax=None,
                           region_xlim=(-90, -40), region_ylim=(-90, 90)):

    # Calcular promedio mensual (primer mes del dataset)
    presion_mean = cloud_data_ds[variable].resample(time='ME').mean()[0, :, :]

    plt.rcParams["figure.figsize"] = (14, 6.5)
    ax = plt.subplot(projection=ccrs.PlateCarree())

    # Normalización de colores
    norm = mcolors.Normalize(
        vmin=vmin if vmin is not None else presion_mean.min().values,
        vmax=vmax if vmax is not None else presion_mean.max().values
    )

    # Mapa de colores
    pm = ax.pcolormesh(presion_mean["lon"], presion_mean["lat"], presion_mean,
                       cmap='viridis', transform=ccrs.PlateCarree(), norm=norm)

    # Contornos (opcional, para resaltar gradientes)
    plt.contour(presion_mean['lon'], presion_mean['lat'], presion_mean,
                colors='black', linewidths=0.5, transform=ccrs.PlateCarree())

    # Elementos del mapa
    ax.coastlines()
    ax.gridlines(draw_labels=True)
    ax.add_feature(cfeature.STATES)
    ax.set_xlim(region_xlim)
    ax.set_ylim(region_ylim)

    # Barra de color
    cbar = plt.colorbar(pm, ax=ax)
    cbar.set_label('Surface Pressure (Pa)')

    # Título
    plt.suptitle(titulo, fontsize=11.5)

    plt.tight_layout(rect=[0, 0.05, 1, 0.95])

    # Guardar gráfico
    plt.savefig("./imagenes/"+nombre_salida, dpi=300)
    print(f"✅ Gráfico guardado en {nombre_salida}")

    plt.show()
    plt.close()

def graficar_viento_u10m(cloud_data_ds, variable='U10M',
                         titulo="M2T1NXSLV.5.12.4 Mean Zonal Wind (U10M) ",
                         nombre_salida="viento_u10m.png",
                         vmin=None, vmax=None,
                         region_xlim=(-90, -40), region_ylim=(-60, 20)):
    
    # Calcular promedio mensual del campo de viento
    viento_mean = cloud_data_ds[variable].resample(time='ME').mean()[0, :, :]

    plt.rcParams["figure.figsize"] = (14, 6.5)
    ax = plt.subplot(projection=ccrs.PlateCarree())

    # Normalización con centro en 0 (viento hacia oeste ↔ este)
    norm = mcolors.TwoSlopeNorm(
        vmin=vmin if vmin is not None else viento_mean.min().values,
        vcenter=0,
        vmax=vmax if vmax is not None else viento_mean.max().values
    )

    # Mapa de colores: azul = viento hacia oeste, rojo = viento hacia este
    pm = ax.pcolormesh(viento_mean["lon"], viento_mean["lat"], viento_mean,
                       cmap='bwr', transform=ccrs.PlateCarree(), norm=norm)

    # Contorno para la línea de calma (0 m/s)
    plt.contour(viento_mean["lon"], viento_mean["lat"], viento_mean,
                levels=[0], colors='purple', linewidths=0.8, transform=ccrs.PlateCarree())

    # Elementos del mapa
    ax.coastlines()
    ax.gridlines(draw_labels=True)
    ax.add_feature(cfeature.STATES)
    ax.set_xlim(region_xlim)
    ax.set_ylim(region_ylim)

    # Leyenda de la línea de calma
    calm_line = mlines.Line2D([], [], color='purple', label='0 m/s Calm Line')
    plt.legend(handles=[calm_line], loc='upper left')

    # Barra de color
    cbar = plt.colorbar(pm, ax=ax)
    cbar.set_label('Zonal Wind (m/s)')

    # Título
    plt.suptitle(titulo, fontsize=11.5)

    plt.tight_layout(rect=[0, 0.05, 1, 0.95])

    # Guardar gráfico
    plt.savefig("./imagenes/"+nombre_salida, dpi=300)
    print(f"✅ Gráfico guardado en {nombre_salida}")
    plt.show()
    plt.close()

@app.get("/calcular_elementos")
def eventos_meteorologicos(lat: float = Query(..., description="Latitude(ej: -75.0)"),
                            lon: float = Query(..., description="Longitude (ej: -53.0)"),
                            fecha_inicio: date = Query(..., description="Fecha de inicio (YYYY-MM-DD)"),
                            fecha_fin: date = Query(..., description="Fecha de fin (YYYY-MM-DD)")):
    try:
        results = earthaccess.search_data(
            short_name="M2T1NXSLV",
            version='5.12.4',
            temporal=(str(fecha_inicio), str(fecha_fin)),
            bounding_box=(lon-20, lat-20, lon+20, lat+20)
        )

        # Parse out URL from request, add to OPeNDAP URLs list for querying multiple granules
        od_files = []
        for item in results:
            for urls in item['umm']['RelatedUrls']:  # Iterate over RelatedUrls in each request step
                if 'OPENDAP' in urls.get('Description', '').upper():  # Check if 'OPENDAP' is in the Description
                    url = urls['URL']
                    # Add URL to list
                    od_files.append(url)

        print('Number of files:', len(od_files))

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            executor.map(download_granule, od_files)

        # Seleccionar solo las variables necesarias
        vars_interes = ['T2M','PS','U10M','lon','lat']

        cloud_data_ds = xr.open_mfdataset(
            'datos_merra_2/*.dap.nc4',
            combine='by_coords',
            chunks={'time': 1}, # Ajusta según memoria,
            preprocess=lambda ds: ds[vars_interes]
        )

        with ProgressBar():
            cloud_data_ds.load()

        ############################################################################################################3

        # Verificar que existen en el dataset
        vars_disponibles = [v for v in vars_interes if v in cloud_data_ds.data_vars]
        print(f"📦 Variables encontradas en el dataset: {vars_disponibles}")

        # Convertir Kelvin → °C si existe T2M
        if 'T2M' in cloud_data_ds:
            cloud_data_ds['T2M'] = cloud_data_ds['T2M'] - 273.15

        # Promediar espacialmente (lon y lat)
        tabla = pd.DataFrame()

        for var in vars_disponibles:
            if 'lon' in var or 'lat' in var:
                continue
            serie = cloud_data_ds[var].mean(dim=['lat', 'lon']).to_pandas()
            tabla[var] = serie

        # Agregar columnas con latitud y longitud promedio (para referencia)
        min_lon, min_lat, max_lon, max_lat = (lon-5, lat-5, lon+5, lat+5)
        tabla['lat'] = (max_lat + min_lat) / 2  # -38.5 aprox.
        tabla['lon'] = (max_lon + min_lon) / 2  # -64.0 aprox.

        # Asegurar que el índice sea la fecha
        tabla.index.name = 'Fecha'

        # 🔹 Agrupar por día y calcular el máximo diario
        tabla_max = tabla.groupby(tabla.index.date).max()

        # Convertir el índice a datetime para mejor formato
        tabla_max.index = pd.to_datetime(tabla_max.index)
        tabla_max.index.name = 'Fecha'

        # Renombrar las columnas agregando el sufijo "_max"
        tabla_max = tabla_max.rename(columns={col: f"{col}_max" for col in tabla_max.columns if col not in ['lat', 'lon']})

        print("\n🧾 Tabla diaria con valores máximos:")
        print(tabla_max.head())
        # Ruta completa donde se guardará el archivo CSV
        # Guardar en CSV
        csv_filename = "tabla_datos_merra2_max_diaria.csv"

        # Ruta completa donde se guardará el archivo CSV
        

        if os.path.exists(csv_filename):
            os.remove(csv_filename)
            print(f"🗑️ Archivo anterior eliminado: {csv_filename}")

        # Guardar el DataFrame como un nuevo archivo CSV
        tabla_max.to_csv("./imagenes/"+csv_filename)

        print(f"✅ Nuevo archivo CSV guardado en: {csv_filename}")
        # Supongamos que tienes un DataFrame 'tabla_max' que deseas guardar

        graficar_temperatura_media(cloud_data_ds,
                                variable='T2M',
                                titulo="Temperatura media y línea de congelación ",
                                nombre_salida="temp_media.png",
                                region_xlim=(lon-10, lon+10),
                                region_ylim=(lat-10, lat+10))

        graficar_presion_media(cloud_data_ds,
                            variable='PS',
                            titulo="Presión superficial media ",
                            nombre_salida="presion_media.png",
                            region_xlim=(lon-10, lon+10),
                            region_ylim=(lat-10, lat+10))

        graficar_viento_u10m(cloud_data_ds,
                            variable='U10M',
                            titulo="Componente zonal del viento (U10M) ",
                            nombre_salida="viento_u10m.png",
                            region_xlim=(lon-10, lon+10),
                            region_ylim=(lat-10, lat+10))
        

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)