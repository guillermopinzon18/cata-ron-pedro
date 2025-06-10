# 🥃 Cata Colaborativa de Ron

Una aplicación web para realizar catas de ron de manera colaborativa y en tiempo real.

## 🌟 Características

- **Navegación por pasos**: Evalúa un ron a la vez
- **Colaborativa**: Todos los participantes ven las respuestas de los demás
- **Actualización automática**: Los resultados se actualizan cada 10 segundos
- **Responsive**: Funciona perfectamente en teléfonos móviles
- **Sin base de datos**: Usa archivos JSON para simplicidad

## 🚀 Cómo usar la aplicación

### Para Participantes:

1. **Accede al link** que te proporcionen
2. **Ingresa tu nombre completo** en el campo de nombre
3. **Evalúa ron por ron**:
   - Completa todas las puntuaciones del ron actual
   - Haz clic en "Guardar y Continuar"
   - Repite para cada ron
4. **Ve los resultados** de todos en tiempo real abajo
5. **Navega hacia atrás** si necesitas cambiar algo

### Para el Organizador:

1. **Comparte el link** de tu aplicación con todos los participantes
2. **Monitorea los resultados** en tiempo real
3. **Limpia datos** si necesitas reiniciar: ve a `/reset`

## 📱 Funcionalidades

### ✅ Navegación por Pasos
- Barra de progreso visual
- Un ron a la vez para mejor concentración
- Botones de navegación anterior/siguiente

### ✅ Colaborativo en Tiempo Real
- Todos ven las respuestas de todos
- Actualización automática cada 10 segundos
- Botón manual de actualización

### ✅ Validación
- Campos obligatorios
- Prevención de pérdida de datos
- Mensajes de error y éxito

### ✅ Responsive
- Optimizado para móviles
- Tablas con scroll horizontal
- Interfaz táctil

## 🛠️ Estructura del Proyecto

```
├── app.py              # Aplicación Flask principal
├── templates/
│   └── index.html      # Interfaz de usuario
├── static/
│   └── style.css       # Estilos CSS
├── requirements.txt    # Dependencias Python
├── vercel.json        # Configuración de Vercel
├── runtime.txt        # Versión de Python
└── cata_data.json     # Datos de la cata (se crea automáticamente)
```

## 🔧 Instalación Local

```bash
# Clonar el repositorio
git clone [tu-repo]
cd Analisis_Ron

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python app.py

# Abrir en el navegador
# http://localhost:5000
```

## 🌐 Despliegue en Vercel

Tu aplicación ya está configurada para Vercel. Solo necesitas:

1. Hacer push de tus cambios a GitHub
2. Vercel se actualizará automáticamente
3. Compartir el link con los participantes

## 📊 Cómo Funciona

### Almacenamiento de Datos
Los datos se guardan en `cata_data.json` con esta estructura:
```json
{
  "Juan Pérez": {
    "A": {
      "pureza": 10,
      "olfato_intensidad": 8,
      "olfato_complejidad": 25,
      "gusto_intensidad": 20,
      "gusto_complejidad": 10,
      "gusto_persistencia": 15,
      "armonia": 10,
      "total": 98,
      "timestamp": "2024-01-15T10:30:00"
    },
    "notas": "Excelente ron con notas a..."
  }
}
```

### Endpoints

- `/` - Página principal con formulario
- `/resultados` - API para obtener datos actualizados (JSON)
- `/reset` - Limpiar todos los datos (solo para desarrollo)

## 🎯 Puntuación

### Criterios de Evaluación:
- **Vista - Pureza**: 0-10 puntos
- **Olfato - Intensidad**: 0-10 puntos  
- **Olfato - Complejidad**: 0-25 puntos
- **Gusto - Intensidad**: 0-20 puntos
- **Gusto - Complejidad**: 0-10 puntos
- **Gusto - Persistencia**: 0-15 puntos
- **Juicio Global - Armonía**: 0-10 puntos

**Total máximo**: 100 puntos

## 🔄 Funciones Automáticas

- **Auto-guardado**: Los datos se guardan inmediatamente
- **Auto-actualización**: Resultados se actualizan cada 10 segundos
- **Prevención de pérdida**: Alerta antes de salir sin guardar
- **Validación en tiempo real**: Campos obligatorios marcados

## 📱 Optimizado para Móviles

- Diseño responsive
- Tablas con scroll horizontal
- Botones táctiles grandes
- Interfaz intuitiva

## ⚡ Características Técnicas

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript vanilla
- **Almacenamiento**: JSON files (sin base de datos)
- **Despliegue**: Vercel
- **Tiempo real**: Polling cada 10 segundos

## 🐛 Solución de Problemas

### No veo las respuestas de otros
- Verifica que tengas conexión a internet
- Haz clic en "🔄 Actualizar"
- La página se actualiza automáticamente cada 30 segundos

### Perdí mi progreso
- Los datos se guardan automáticamente al hacer clic en "Guardar y Continuar"
- Puedes usar "← Paso Anterior" para revisar

### La aplicación está lenta
- Es normal con muchos usuarios simultáneos
- Los datos se sincronizan cada 10 segundos

## 📞 Soporte

Si tienes problemas:
1. Recarga la página
2. Verifica tu conexión a internet
3. Contacta al organizador de la cata

---

¡Disfruta tu cata de ron! 🥃✨
