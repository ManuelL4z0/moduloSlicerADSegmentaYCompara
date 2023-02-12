# moduloSlicerADSegmentaYCompara
Módulo en Python para la asistencia a la segmentación y comparación de estructuras del cerebro en 3D Slicer. Desarrollado en el marco del MIBSD de la US. Funcionando en Slicer 5.0.3 y Python 3.9.10

Puede instalarse como cualquier extensión al incluirla en el directorio que Slicer usa para gestionarlas. Seguidamente será necesario seleccionarla desde Slicer con el 'Extension Wizard' dentro de las 'Developer Tools'.

El módulo ofrece la posibilidad de usar dos herramientas de segmentación:
  -La primera, basada en crecimiento de semillas intenta agilizar este proceso al aglutinar también las herramientas de dibujo. Se crean dos segmentos ('Cerebro' y 'NoCerebro') que pueden intercambiarse con las teclas '1' y '2' del teclado. Además se puede cambiar el tamaño del pincel con la macro 'Shift+RuedaRatón'. Una vez se comienza a generar contenido en ambos segmentos es posible activar la previsualización y aplicarla cuando se considere correcta.
    -La segunda, basada en umbralización consiste en 4 pasos: primero se debe umbralizar hasta capturar toda la masa cerebral, luego se realiza una erosión, se sigue con una separación en elementos conexos que retiene la isla de mayor tamaño y finalmente se hace una dilatación con un kernel igual al usado en la erosión.

Además tiene una última sección que calcula el volumen de todos los segmentos visibles en el nodod de segmentación generado por el módulo. Esta última parte es fácilmente adaptable a las necesidades del usuario.
