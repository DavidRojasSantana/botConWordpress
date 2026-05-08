# presentation/menus.py – Constructores de mensajes y menús del chatbot
from datetime import datetime
from config import SERVICE_LABELS, ENGINEER_EMAIL, EMAIL_SENDER

# ── CAMBIO: Importamos el servicio de Telegram ──
from services.whatsapp import send_telegram
from services.email import send_email
import core.state as state

def menu1(user_number: str) -> None:
    texto = (
        'Bienvenido/a, este canal corresponde a un asistente virtual automatizado de Proyectos Web\n'
        'Tenga en cuenta que no está interactuando con una persona real. Nuestro asistente está\n'
        'diseñado para brindarle información y gestionar solicitudes específicas\n'
        'Para comunicarse con este chat solo digite el numero de las opciones sin puntos ni espacios\n\n'
        'Bienvenido a Proyectos Web, donde diseñamos tu presencia digital.\n\n'
        'Estas son las opciones que podemos ofrecer:\n\n'
        '1- Conocer nuestros servicios\n'
        '2- Agendar una cita'
    )
    imagen = 'https://raw.githubusercontent.com/DavidRojasSantana/imagenes/refs/heads/main/logo1.jpg'
    send_telegram(user_number, texto, imagen)
    state.set_state(user_number, 'main')


def subMenu1(user_number: str) -> None:
    send_telegram(
        user_number,
        'Estos son los servicios que ofrecemos:\n\n'
        '1- Desarrollo de páginas o aplicaciones web\n'
        '2- Mantenimiento y soporte de software\n'
        '3- Chatbot para WhatsApp\n'
        '0- Volver al menú anterior'
    )
    state.set_state(user_number, 'services')


def subMenu1_2(user_number: str) -> None:
    send_telegram(
        user_number,
        'En páginas o aplicaciones web tenemos:\n\n'
        '1- Páginas one page\n'
        '2- Páginas multi page\n'
        '3- Aplicaciones web\n'
        '0- Volver al menú anterior'
    )
    state.set_state(user_number, 'web_dev')


def onePage(user_number: str) -> None:
    texto = (
        'Páginas One page\n\n'
        'Es toda la información de tu empresa en una sola página y se '
        'visualiza con scroll vertical. Navegación mediante anclas internas (por ejemplo, '
        'al hacer clic en "Servicios", la página se desplaza hacia esa sección).\n'
        'Estructura simple, limpia que ofrece un diseño bastante atractivo y funcional.\n\n'
        '1- Hablar con un Ingeniero\n'
        '2- Agendar una cita\n'
        '0- Volver al menú anterior'
    )
    imagen = ('https://static.wixstatic.com/media/'
              '110ec7_b1bfbd18053d42b3a863cc7800ef6638~mv2.png/'
              'v1/fill/w_740,h_423,al_c,q_85,usm_0.66_1.00_0.01,'
              'enc_avif,quality_auto/'
              '110ec7_b1bfbd18053d42b3a863cc7800ef6638~mv2.png')
    send_telegram(user_number, texto, imagen)
    state.set_state(user_number, 'sub_menu_one_page')


def multiPage(user_number: str) -> None:
    send_telegram(
        user_number,
        'Páginas Multi page\n\n'
        'Es la información de tu empresa. Contiene varias páginas '
        'independientes, como home, servicios, contacto, etc.\n\n'
        '1- Hablar con el Ingeniero\n'
        '2- Agendar una cita\n'
        '0- Volver al menú anterior'
    )
    state.set_state(user_number, 'sub_menu_multi_page')


def appWeb(user_number: str) -> None:
    texto = (
        'Aplicación web\n\n'
        'Es un diseño más profesional donde necesitas hacer '
        'venta de un producto en específico y un aplicativo que no solo le permita '
        'mostrar si no que pueda gestionar su inventario y su negocio.\n\n'
        '1- Hablar con un Ingeniero\n'
        '2- Agendar una cita\n'
        '0- Volver al menú anterior'
    )
    imagen = 'https://mrhouston.net/wp-content/uploads/2018/03/Aplicaciones-Web.png'
    send_telegram(user_number, texto, imagen)
    state.set_state(user_number, 'sub_menu_web_app')


def subMenu2(user_number: str) -> None:
    send_telegram(
        user_number,
        'En mantenimiento y software tenemos:\n\n'
        '1- Optimización del Sistema y Rendimiento\n'
        '2- Seguridad y Eliminación de Malware\n'
        '3- Soporte de Software y Aplicaciones\n'
        '4- Soporte y Asesoramiento Remoto\n'
        '0- Volver al menú anterior'
    )
    state.set_state(user_number, 'maintenance')


def optimizaSistemaRendimiento(user_number: str) -> None:
    imagen = 'https://cdn.pixabay.com/photo/2021/07/10/18/24/gears-6402028_640.jpg'
    send_telegram(
        user_number,
        'Optimización del sistema y rendimiento:\n\n'
        'Realizo un diagnóstico exhaustivo para identificar los cuellos de botella de tu equipo, '
        'como los programas que consumen más recursos o los archivos innecesarios que ocupan espacio. '
        'Luego, realizo una limpieza profunda para eliminar el caché y los archivos temporales, y gestiono '
        'los programas que se inician automáticamente para que tu portátil arranque mucho más rápido. '
        'También me aseguro de que todos los controladores estén actualizados.\n\n'
        '1- Hablar con un asesor.\n'
        '2- Agendar una cita.\n'
        '0- Volver al menú anterior',
        imagen
    )
    state.set_state(user_number, 'opsisren')


def seguridadEliminacionMalware(user_number: str) -> None:
    imagen = 'https://cdn.pixabay.com/photo/2024/05/23/12/24/ai-generated-8783105_640.jpg'
    send_telegram(
        user_number,
        'Seguridad y Eliminación de Malware:\n\n'
        'Entiendo que la protección de tu información es fundamental, por eso ofrezco servicios '
        'de eliminación de malware y virus. Escaneo tu sistema a fondo para detectar y erradicar '
        'cualquier amenaza, como virus, troyanos o spyware. Si no tienes un antivirus, te asesoro '
        'para elegir e instalar el más adecuado, asegurándome de que tu equipo esté protegido.\n\n'
        '1- Hablar con un asesor.\n'
        '2- Agendar una cita.\n'
        '0- Volver al menú anterior',
        imagen
    )
    state.set_state(user_number, 'seguElimMa')


def soporteSoftApps(user_number: str) -> None:
    imagen = 'https://cdn.pixabay.com/photo/2018/07/12/21/32/subscribe-3534409_640.jpg'
    send_telegram(
        user_number,
        'Soporte de Software y Aplicaciones:\n\n'
        'Te ayudo a instalar y configurar software, resuelvo los conflictos que '
        'causan que tus programas se bloqueen, y me encargo de que tu sistema operativo '
        'esté siempre actualizado para funcionar con la máxima estabilidad.\n\n'
        '1- Hablar con un asesor.\n'
        '2- Agendar una cita.\n'
        '0- Volver al menú anterior',
        imagen
    )
    state.set_state(user_number, 'soprtSofApps')


def remoto(user_number: str) -> None:
    imagen = 'https://cdn.pixabay.com/photo/2025/08/04/05/50/ai-generated-9753236_640.jpg'
    send_telegram(
        user_number,
        'Soporte y Asesoramiento Remoto:\n\n'
        'Te ofrezco mi ayuda para resolver los problemas de software sin que tengas que moverte, '
        'usando una conexión remota segura con programas como TeamViewer o AnyDesk.\n\n'
        '1- Hablar con el Ingeniero.\n'
        '2- Agendar una cita.\n'
        '0- Volver al menú anterior',
        imagen
    )
    state.set_state(user_number, 'remoto')


def subMenu3(user_number: str) -> None:
    imagen = 'https://cdn.pixabay.com/photo/2023/03/31/07/26/artificial-intelligence-7889375_640.jpg'
    send_telegram(
        user_number,
        'Un chatbot\n\n'
        'Es un programa de software diseñado para simular una conversación humana. '
        'Funciona mediante reglas predefinidas o inteligencia artificial (IA) para interactuar '
        'con los usuarios a través de plataformas de mensajería como WhatsApp, etc. Su objetivo '
        'principal es automatizar tareas y responder preguntas de manera rápida y eficiente, '
        'sin necesidad de intervención humana. Como este servicio que interactúa contigo, '
        'puede ser una herramienta importante en tu negocio.\n\n'
        '1- Hablar con el Ingeniero.\n'
        '2- Agendar una cita.\n'
        '0- Volver al menú anterior',
        imagen
    )
    state.set_state(user_number, 'chatbot_info')


def hablarAsesor(user_number: str, servicio: str = '') -> None:
    imagen = 'https://cdn.pixabay.com/photo/2020/07/25/17/39/computer-5437373_640.jpg'
    send_telegram(
        user_number,
        'Claro, puedes comunicarte directamente con nuestro Ingeniero. Escríbele o llámalo:\n'
        '+57 310 7791984\n'
        '¡Esperamos poder ayudarte!\n\n'
        'Escribe "hola" para volver al menú principal.',
        imagen
    )
    state.set_state(user_number, 'start')

    # Notificar al ingeniero con el resumen del cliente
    dest    = ENGINEER_EMAIL or EMAIL_SENDER
    srv_txt = (servicio if servicio
               else 'No especificó (solicitó contacto directo desde el menú principal)')
    ahora   = datetime.now().strftime('%d/%m/%Y %H:%M')

    print(f"[hablarAsesor] Cliente +{user_number} | Servicio: {srv_txt}", flush=True)
    print(f"[hablarAsesor] Notificando al ingeniero → {dest}", flush=True)

    ok = send_email(
        dest,
        f'Nuevo cliente interesado – {srv_txt}',
        f'Hola,\n\n'
        f'Un cliente quiere contactarte directamente a través del chatbot.\n\n'
        f'📱 WhatsApp: +{user_number}\n'
        f'🔧 Servicio de interés: {srv_txt}\n'
        f'🕐 Fecha y hora del contacto: {ahora}\n\n'
        f'Te recomendamos responderle lo antes posible.\n\n'
        f'— Chatbot de Proyectos Web'
    )
    print(f"[hablarAsesor] Email al ingeniero: {'✅ enviado' if ok else '❌ falló'}", flush=True)
