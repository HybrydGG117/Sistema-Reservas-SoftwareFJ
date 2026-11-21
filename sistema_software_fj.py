from abc import ABC, abstractmethod
from datetime import datetime
import logging

# ==============================================================================
# 1. CONFIGURACIÓN DEL SISTEMA DE LOGS (REGISTRO DE EVENTOS Y ERRORES)
# ==============================================================================
logging.basicConfig(
    filename="registro_eventos.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)

def registrar_evento(mensaje: str, es_error: bool = False):
    """Registra eventos y errores tanto en el archivo .log como en consola."""
    if es_error:
        logging.error(mensaje)
        print(f"[ERROR REGISTRADO] {mensaje}")
    else:
        logging.info(mensaje)
        print(f"[INFO] {mensaje}")


# ==============================================================================
# 2. EXCEPCIONES PERSONALIZADAS
# ==============================================================================
class ErrorSistemaFJ(Exception):
    """Excepción base para todos los errores del sistema Software FJ."""
    pass

class DatoInvalidoError(ErrorSistemaFJ):
    """Se lanza cuando un dato de entrada no cumple con las validaciones."""
    pass

class ServicioNoDisponibleError(ErrorSistemaFJ):
    """Se lanza cuando el servicio solicitado no está activo o disponible."""
    pass

class ReservaInvalidaError(ErrorSistemaFJ):
    """Se lanza ante inconsistencias o fallos al procesar una reserva."""
    pass


# ==============================================================================
# 3. CLASE ABSTRACTA BASE PARA ENTIDADES DEL SISTEMA
# ==============================================================================
class EntidadSistema(ABC):
    """Clase abstracta general que representa cualquier entidad del sistema."""

    def __init__(self, id_entidad: str):
        if not id_entidad or not id_entidad.strip():
            raise DatoInvalidoError("El identificador de la entidad no puede estar vacío.")
        self._id = id_entidad.strip()
        self._fecha_registro = datetime.now()

    @property
    def id(self) -> str:
        return self._id

    @abstractmethod
    def obtener_resumen(self) -> str:
        """Método abstracto que obliga a las clases hijas a describirse."""
        pass


# ==============================================================================
# 4. CLASE CLIENTE (ENCAPSULACIÓN Y VALIDACIONES ESTRICTAS)
# ==============================================================================
class Cliente(EntidadSistema):
    """Representa un cliente de Software FJ con atributos privados y validados."""

    def __init__(self, id_cliente: str, nombre: str, documento: str, correo: str):
        super().__init__(id_cliente)
        self.nombre = nombre
        self.documento = documento
        self.correo = correo

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or len(valor.strip()) < 3:
            raise DatoInvalidoError(f"Nombre inválido: '{valor}'. Debe tener al menos 3 caracteres.")
        self.__nombre = valor.strip()

    @property
    def documento(self) -> str:
        return self.__documento

    @documento.setter
    def documento(self, valor: str):
        if not valor or not valor.strip().isdigit() or len(valor.strip()) < 5:
            raise DatoInvalidoError(f"Documento inválido: '{valor}'. Debe ser numérico de mínimo 5 dígitos.")
        self.__documento = valor.strip()

    @property
    def correo(self) -> str:
        return self.__correo

    @correo.setter
    def correo(self, valor: str):
        if not valor or "@" not in valor or "." not in valor:
            raise DatoInvalidoError(f"Correo electrónico inválido: '{valor}'.")
        self.__correo = valor.strip().lower()

    def obtener_resumen(self) -> str:
        return f"Cliente [{self.id}] {self.nombre} | Doc: {self.documento} | Email: {self.correo}"


# ==============================================================================
# 5. CLASE ABSTRACTA SERVICIO Y SUS 3 CLASES DERIVADAS (POLIMORFISMO)
# ==============================================================================
class Servicio(EntidadSistema, ABC):
    """Clase abstracta base para los servicios ofrecidos por Software FJ."""

    def __init__(self, id_servicio: str, nombre_servicio: str, tarifa_base: float, disponible: bool = True):
        super().__init__(id_servicio)
        if not nombre_servicio or not nombre_servicio.strip():
            raise DatoInvalidoError("El nombre del servicio no puede estar vacío.")
        if tarifa_base <= 0:
            raise DatoInvalidoError(f"La tarifa base ({tarifa_base}) debe ser mayor a cero.")

        self._nombre_servicio = nombre_servicio.strip()
        self._tarifa_base = float(tarifa_base)
        self._disponible = disponible

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, estado: bool):
        self._disponible = bool(estado)

    @abstractmethod
    def validar_parametros(self, duracion_horas: int) -> None:
        pass

    @abstractmethod
    def calcular_costo(self, duracion_horas: int) -> float:
        pass

    @abstractmethod
    def describir_servicio(self) -> str:
        pass

    # Método sobrecargado (mediante parámetros opcionales) para cálculo final con impuestos/descuentos
    def calcular_total_facturacion(self, duracion_horas: int, descuento_pct: float = 0.0, aplicar_iva: bool = True) -> float:
        """
        Sobrecarga funcional: permite calcular solo costo base, con descuento,
        con IVA (19%) o ambos según los argumentos enviados.
        """
        if descuento_pct < 0 or descuento_pct > 100:
            raise DatoInvalidoError(f"Porcentaje de descuento fuera de rango (0-100): {descuento_pct}")

        subtotal = self.calcular_costo(duracion_horas)
        monto_descuento = subtotal * (descuento_pct / 100.0)
        base_gravable = subtotal - monto_descuento
        iva = base_gravable * 0.19 if aplicar_iva else 0.0
        return round(base_gravable + iva, 2)

    def obtener_resumen(self) -> str:
        return self.describir_servicio()


class ReservaSala(Servicio):
    """Servicio especializado: Alquiler de salas tecnológicas o de reuniones."""

    def __init__(self, id_servicio: str, nombre_servicio: str, tarifa_base: float, capacidad: int, disponible: bool = True):
        super().__init__(id_servicio, nombre_servicio, tarifa_base, disponible)
        if capacidad <= 0:
            raise DatoInvalidoError("La capacidad de la sala debe ser mayor a 0 personas.")
        self.capacidad = capacidad

    def validar_parametros(self, duracion_horas: int) -> None:
        if duracion_horas < 1 or duracion_horas > 12:
            raise DatoInvalidoError("La reserva de sala debe ser entre 1 y 12 horas.")

    def calcular_costo(self, duracion_horas: int) -> float:
        self.validar_parametros(duracion_horas)
        recargo_capacidad = 15000.0 if self.capacidad > 20 else 0.0
        return (self._tarifa_base * duracion_horas) + recargo_capacidad

    def describir_servicio(self) -> str:
        return f"Sala [{self.id}]: {self._nombre_servicio} (Capacidad: {self.capacidad} pers.) - Base: ${self._tarifa_base:,.0f}/h"


class AlquilerEquipo(Servicio):
    """Servicio especializado: Alquiler de equipos de cómputo o servidores."""

    def __init__(self, id_servicio: str, nombre_servicio: str, tarifa_base: float, gama: str, disponible: bool = True):
        super().__init__(id_servicio, nombre_servicio, tarifa_base, disponible)
        if gama.lower() not in ("estandar", "profesional", "servidor"):
            raise DatoInvalidoError(f"Gama de equipo no válida: '{gama}'. Use: estandar, profesional o servidor.")
        self.gama = gama.lower()

    def validar_parametros(self, duracion_horas: int) -> None:
        if duracion_horas < 2:
            raise DatoInvalidoError("El alquiler de equipos requiere un mínimo de 2 horas.")

    def calcular_costo(self, duracion_horas: int) -> float:
        self.validar_parametros(duracion_horas)
        multiplicador = {"estandar": 1.0, "profesional": 1.25, "servidor": 1.5}[self.gama]
        return self._tarifa_base * duracion_horas * multiplicador

    def describir_servicio(self) -> str:
        return f"Equipo [{self.id}]: {self._nombre_servicio} (Gama: {self.gama.capitalize()}) - Base: ${self._tarifa_base:,.0f}/h"


class AsesoriaEspecializada(Servicio):
    """Servicio especializado: Consultoría en ingeniería y arquitectura de software."""

    def __init__(self, id_servicio: str, nombre_servicio: str, tarifa_base: float, especialidad: str, disponible: bool = True):
        super().__init__(id_servicio, nombre_servicio, tarifa_base, disponible)
        if not especialidad or not especialidad.strip():
            raise DatoInvalidoError("Debe indicar la especialidad de la asesoría.")
        self.especialidad = especialidad.strip()

    def validar_parametros(self, duracion_horas: int) -> None:
        if duracion_horas < 1 or duracion_horas > 8:
            raise DatoInvalidoError("Las asesorías especializadas se agendan entre 1 y 8 horas por sesión.")

    def calcular_costo(self, duracion_horas: int) -> float:
        self.validar_parametros(duracion_horas)
        # Tarifa fija de diagnóstico inicial + valor por hora
        tarifa_diagnostico = 30000.0
        return tarifa_diagnostico + (self._tarifa_base * duracion_horas)

    def describir_servicio(self) -> str:
        return f"Asesoría [{self.id}]: {self._nombre_servicio} (Área: {self.especialidad}) - Base: ${self._tarifa_base:,.0f}/h"


# ==============================================================================
# 6. CLASE RESERVA (GESTIÓN DE ESTADOS Y MANEJO AVANZADO DE EXCEPCIONES)
# ==============================================================================
class Reserva(EntidadSistema):
    """Integra Cliente, Servicio, duración y estado con control estricto de errores."""

    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio, duracion_horas: int):
        super().__init__(id_reserva)
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("Se requiere una instancia válida de Cliente.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("Se requiere una instancia válida de Servicio.")

        self.cliente = cliente
        self.servicio = servicio
        self.duracion_horas = duracion_horas
        self.estado = "PENDIENTE"
        self.costo_total = 0.0

    def procesar_y_confirmar(self, descuento_pct: float = 0.0, aplicar_iva: bool = True) -> None:
        """
        Procesa el costo y confirma la reserva usando try/except/else/finally
        y encadenamiento de excepciones (raise ... from ...).
        """
        try:
            if self.estado == "CANCELADA":
                raise ReservaInvalidaError(f"La reserva {self.id} ya está cancelada y no puede confirmarse.")
            if not self.servicio.disponible:
                raise ServicioNoDisponibleError(f"El servicio '{self.servicio._nombre_servicio}' no está disponible actualmente.")

            # Cálculo usando sobrecarga de parámetros
            self.costo_total = self.servicio.calcular_total_facturacion(
                self.duracion_horas,
                descuento_pct=descuento_pct,
                aplicar_iva=aplicar_iva
            )
        except ErrorSistemaFJ as err:
            self.estado = "RECHAZADA"
            # Encadenamiento explícito de excepciones
            raise ReservaInvalidaError(f"Fallo al procesar la reserva {self.id} para {self.cliente.nombre}.") from err
        else:
            self.estado = "CONFIRMADA"
            registrar_evento(
                f"Reserva {self.id} CONFIRMADA | Cliente: {self.cliente.nombre} | "
                f"{self.servicio.describir_servicio()} | Horas: {self.duracion_horas} | Total: ${self.costo_total:,.2f}"
            )
        finally:
            registrar_evento(f"Auditoría de ejecución finalizada para reserva {self.id} (Estado actual: {self.estado}).")

    def cancelar(self) -> None:
        if self.estado == "CANCELADA":
            raise ReservaInvalidaError(f"La reserva {self.id} ya se encontraba cancelada.")
        self.estado = "CANCELADA"
        registrar_evento(f"Reserva {self.id} CANCELADA por solicitud del sistema/cliente.")

    def obtener_resumen(self) -> str:
        return (f"Reserva [{self.id}] | Estado: {self.estado} | Cliente: {self.cliente.nombre} | "
                f"Servicio: {self.servicio._nombre_servicio} | Total: ${self.costo_total:,.2f}")


# ==============================================================================
# 7. GESTOR DEL SISTEMA EN MEMORIA (LISTAS INTERNAS, SIN BASE DE DATOS)
# ==============================================================================
class SistemaSoftwareFJ:
    """Controlador principal que almacena los objetos en listas en memoria."""

    def __init__(self):
        self.clientes: list[Cliente] = []
        self.servicios: list[Servicio] = []
        self.reservas: list[Reserva] = []

    def registrar_cliente(self, id_c: str, nombre: str, doc: str, correo: str):
        try:
            nuevo_cliente = Cliente(id_c, nombre, doc, correo)
            self.clientes.append(nuevo_cliente)
            registrar_evento(f"Cliente registrado exitosamente: {nuevo_cliente.obtener_resumen()}")
            return nuevo_cliente
        except ErrorSistemaFJ as e:
            registrar_evento(f"Error registrando cliente [{id_c}]: {e}", es_error=True)
            return None

    def registrar_servicio(self, servicio_obj_fn):
        try:
            servicio = servicio_obj_fn()
            self.servicios.append(servicio)
            registrar_evento(f"Servicio creado exitosamente: {servicio.describir_servicio()}")
            return servicio
        except ErrorSistemaFJ as e:
            registrar_evento(f"Error creando servicio: {e}", es_error=True)
            return None

    def crear_y_procesar_reserva(self, id_r: str, cliente: Cliente, servicio: Servicio, horas: int, desc: float = 0.0, iva: bool = True):
        try:
            reserva = Reserva(id_r, cliente, servicio, horas)
            reserva.procesar_y_confirmar(descuento_pct=desc, aplicar_iva=iva)
            self.reservas.append(reserva)
            return reserva
        except ErrorSistemaFJ as e:
            causa = f" -> Causa raíz: {e.__cause__}" if e.__cause__ else ""
            registrar_evento(f"Excepción controlada en reserva [{id_r}]: {e}{causa}", es_error=True)
            return None


# ==============================================================================
# 8. SIMULACIÓN DE 12 OPERACIONES COMPLETAS (VÁLIDAS E INVÁLIDAS)
# ==============================================================================
def ejecutar_simulacion():
    print("=" * 80)
    print(" INICIANDO SISTEMA INTEGRAL DE GESTIÓN - SOFTWARE FJ (UNAD 213023) ")
    print("=" * 80)

    sistema = SistemaSoftwareFJ()

    # --- OPERACIÓN 1: Registro válido de cliente 1 ---
    c1 = sistema.registrar_cliente("CLI-01", "Laura Martínez", "1075234890", "laura.martinez@correo.com")

    # --- OPERACIÓN 2: Registro válido de cliente 2 ---
    c2 = sistema.registrar_cliente("CLI-02", "Carlos Gómez", "79456123", "carlos.gomez@empresa.co")

    # --- OPERACIÓN 3: Registro INVÁLIDO de cliente (correo sin @ y documento corto) ---
    sistema.registrar_cliente("CLI-03", "Ana", "12", "correo_invalido.com")

    # --- OPERACIÓN 4: Creación válida de Servicio 1 (Reserva de Sala) ---
    s1 = sistema.registrar_servicio(lambda: ReservaSala("SRV-01", "Sala Innovación Cloud", 80000, capacidad=25))

    # --- OPERACIÓN 5: Creación válida de Servicio 2 (Alquiler de Equipo) ---
    s2 = sistema.registrar_servicio(lambda: AlquilerEquipo("SRV-02", "Workstation Dell Precision", 45000, gama="profesional"))

    # --- OPERACIÓN 6: Creación válida de Servicio 3 (Asesoría Especializada - No disponible) ---
    s3 = sistema.registrar_servicio(lambda: AsesoriaEspecializada("SRV-03", "Arquitectura Microservicios", 120000, "DevOps", disponible=False))

    # --- OPERACIÓN 7: Creación INVÁLIDA de servicio (tarifa negativa) ---
    sistema.registrar_servicio(lambda: ReservaSala("SRV-04", "Sala Fantasma", -50000, capacidad=10))

    # --- OPERACIÓN 8: Reserva EXITOSA de Sala (con descuento del 10% e IVA) ---
    r1 = sistema.crear_y_procesar_reserva("RES-01", c1, s1, horas=4, desc=10.0, iva=True)

    # --- OPERACIÓN 9: Reserva EXITOSA de Equipo (sin descuento, sin IVA - sobrecarga) ---
    r2 = sistema.crear_y_procesar_reserva("RES-02", c2, s2, horas=5, desc=0.0, iva=False)

    # --- OPERACIÓN 10: Reserva FALLIDA por servicio NO DISPONIBLE (Encadenamiento) ---
    sistema.crear_y_procesar_reserva("RES-03", c1, s3, horas=3)

    # --- OPERACIÓN 11: Reserva FALLIDA por duración inválida (Equipo mínimo 2 horas) ---
    sistema.crear_y_procesar_reserva("RES-04", c2, s2, horas=1)

    # --- OPERACIÓN 12: Cancelación de reserva válida y prueba de doble cancelación controlada ---
    if r2:
        try:
            r2.cancelar()
            r2.cancelar()  # Intento duplicado que dispara excepción controlada
        except ErrorSistemaFJ as e:
            registrar_evento(f"Error controlado al intentar cancelar nuevamente: {e}", es_error=True)

    # ==========================================================================
    # REPORTE FINAL EN MEMORIA
    # ==========================================================================
    print("\n" + "=" * 80)
    print(" RESUMEN FINAL EN MEMORIA (SISTEMA OPERATIVO SIN INTERRUPCIONES) ")
    print("=" * 80)
    print(f"Total Clientes válidos en lista : {len(sistema.clientes)}")
    print(f"Total Servicios válidos en lista: {len(sistema.servicios)}")
    print(f"Total Reservas exitosas en lista: {len(sistema.reservas)}")
    for res in sistema.reservas:
        print("  ->", res.obtener_resumen())
    print("\nRevise el archivo 'registro_eventos.log' generado en esta carpeta para ver la auditoría completa.")


if __name__ == "__main__":
    ejecutar_simulacion()
