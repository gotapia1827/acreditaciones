import re
from django.core.exceptions import ValidationError


def validar_rut_chileno(rut):
    """
    Valida RUT chileno.
    Formatos aceptados: 12345678-9, 12.345.678-9
    """
    if not rut:
        return

    # Limpiar puntos y espacios
    rut_limpio = rut.replace('.', '').replace(' ', '').upper()

    # Verificar formato básico
    if not re.match(r'^\d{7,8}-[\dK]$', rut_limpio):
        raise ValidationError(
            'RUT inválido. Formato esperado: 12345678-9 o 12.345.678-9'
        )

    # Separar número y dígito verificador
    partes = rut_limpio.split('-')
    numero = int(partes[0])
    dv_ingresado = partes[1]

    # Calcular dígito verificador
    dv_calculado = _calcular_dv(numero)

    if dv_ingresado != dv_calculado:
        raise ValidationError('RUT inválido. El dígito verificador no coincide.')


def _calcular_dv(numero):
    """Calcula el dígito verificador de un RUT chileno."""
    reversed_digits = map(int, reversed(str(numero)))
    factors = [2, 3, 4, 5, 6, 7]
    total = sum(d * factors[i % 6] for i, d in enumerate(reversed_digits))
    remainder = 11 - (total % 11)
    if remainder == 11:
        return '0'
    if remainder == 10:
        return 'K'
    return str(remainder)