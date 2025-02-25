Carroponte Pipeline - Estructura y Uso de Módulos
Este documento explica la forma de organizar los pasos (Steps) del pipeline en archivos separados y cómo aprovechar los módulos ya existentes en el repositorio (data/, processing/, ui/, utils/, etc.) para cada fase de la calibración y procesamiento de imágenes en el proyecto Carroponte.

1. Estructura de Carpetas
Propuesta de organización para ubicar la lógica de cada paso (StepXX) en un script separado, y un archivo principal main.py que coordina todo a través de una interfaz con pestañas (tabs) en Gradio.

sql
Copy
Edit
├── main.py                     <-- Interfaz principal (Gradio) con tabs para cada Step
├── scripts
│   ├── step01_update_json.py   <-- Step 01: Leer .txt y actualizar JSON
│   ├── step02_visualize.py     <-- Step 02: Visualizar JSON y .txt
│   ├── step03_estimate_center.py
│   ├── step04_visual_calib.py
│   ├── step05_interpolation.py
│   ├── step06_orientation_propagation.py
│   ├── step07_display_comparison.py
│   └── step08_export_csv.py
├── data
│   ├── ground_truth
│   │   ├── all_sequences.json
│   │   └── ...
│   ├── json_handler.py         <-- Manejo de lectura/escritura y actualización de estados en JSON
│   ├── pix4d_export.py         <-- Export a CSV en formato Pix4D
│   ├── pix4d_import.py         <-- Import de parámetros calibrados Pix4D
│   ├── preprocessing.py
│   └── sequence_handler.py
├── processing
│   ├── angular_transform.py    <-- Conversión ángulo <-> (x,y)
│   ├── circle_estimator.py     <-- Cálculo de centro/radio
│   ├── cluster_calibrator.py
│   ├── orientation_corrector.py
│   ├── position_estimator.py
│   ├── short_arc_interpolator.py
│   └── update_all_sequences.py
├── ui
│   ├── fast_txt_visualizer.py
│   ├── ui_app.py
│   ├── ...
└── utils
    ├── constants.py
    ├── math_utils.py
    └── time_utils.py
main.py:

Presenta una interfaz de usuario con Gradio y pestañas (Tabs), una por cada Step (del 1 al 8).
Cada pestaña invoca una “función de callback” que llama internamente al script correspondiente de scripts/ (por ejemplo, step01_update_json.py) para realizar la lógica del paso.
scripts/:

Archivos stepXX_...py, cada uno con la lógica específica de un Paso del pipeline (Step 01 al Step 08).
Se recomienda que cada archivo contenga una función principal, por ejemplo run_stepXX(...), que reciba los parámetros y ejecute la lógica de ese paso.
data/, processing/, ui/, utils/:

Contienen módulos reutilizables y utilidades ya existentes en el repositorio.
Se pueden (y deben) importar dentro de los scripts de scripts/ para aprovechar la lógica existente (leer/escribir JSON, conversión de ángulos, estimaciones, etc.).
2. Descripción de cada Step (y uso de módulos existentes)
La siguiente tabla describe el objetivo de cada Step y qué módulos ya existentes se pueden reutilizar en su implementación.

Step	Descripción	Módulos Útiles
Step01
step01_update_json.py	Lectura de un archivo .txt de calibración (por ejemplo, con posiciones X, Y, Z y orientación Omega, Phi, Kappa) y actualización del JSON principal.
- Marca las imágenes encontradas como calibrated, y las que no están, como uncalibrated.	- data/json_handler.py: para cargar/guardar JSON, setear campos.
- data/pix4d_import.py: si el .txt sigue el estándar Pix4D.
Step02
step02_visualize.py	Visualiza el contenido del JSON (posiciones calibradas / no calibradas) y, en paralelo, los datos del .txt (o de otro archivo) en un gráfico Plotly.
- Permite comparar posiciones en 2 subplots (o uno al lado del otro).	- ui/fast_txt_visualizer.py: ejemplos para graficar .txt con Plotly.
- data/json_handler.py: para extraer posiciones del JSON.
Step03
step03_estimate_center.py	Determina el centro y radio de cada secuencia.
- El centro puede calcularse con circle_estimator.py (una vez implementado).
- Se guardan axis_center y calculated_radius en el JSON.	- processing/circle_estimator.py: lógica para estimar el círculo.
- data/json_handler.py: actualizar step_info["axis_center"] y step_info["calculated_radius"].
Step04
step04_visual_calib.py	Calibrar imágenes no calibradas pero presentes en el CSV Visual match IDs to columns.csv.
- Conviertes el valor angular en XY (usando calculated_radius).
- Marcas Calibration_Status = "visually calibrated".	- processing/angular_transform.py: para convertir de ángulo a (x,y).
- data/json_handler.py: marcar como visually calibrated.
- config.py (si tienes VISUAL_MATCH_IDS y el CENTER).
Step05
step05_interpolation.py	Interpolar posiciones de imágenes intermedias entre “original” y “visually calibrated”.
- Distribuirlas equidistantes angularmente y asignarles Calibration_Status = "estimated".	- processing/short_arc_interpolator.py: ejemplo para la interpolación de arcos cortos.
- processing/cluster_calibrator.py: si ya tienes funciones de propagación.
Step06
step06_orientation_propagation.py	Usar OrientationCorrector (o orientation_corrector.py) para propagar la orientación a las nuevas imágenes calibradas o estimadas.
- Asigna Omega, Phi, Kappa usando ángulos polares y/o interpolación.	- processing/orientation_corrector.py: método infer_orientation_from_polar.
- data/json_handler.py.
Step07
step07_display_comparison.py	Mostrar la comparación de posiciones y orientaciones en un gráfico Plotly:
- original (o calibrated), visually calibrated, estimated.
- Marcar distintos colores, vectores de orientación, etc.	- visualization/plotter.py: ya tienes ejemplos de cómo hacer plots con varias categorías.
- ui/fast_txt_visualizer.py: si te ayuda a superponer.
Step08
step08_export_csv.py	Exportación final a CSV (por ejemplo, formato Pix4D) con posición y orientación de todas las imágenes.
- Ocurre al final del pipeline.	- data/pix4d_export.py: función export_to_pix4d_csv(all_data, output_csv).
En cada Step, puedes combinar varios módulos. Por ejemplo, Step05 puede usar short_arc_interpolator.py y angular_transform.py para resolver la interpolación de arcos.

