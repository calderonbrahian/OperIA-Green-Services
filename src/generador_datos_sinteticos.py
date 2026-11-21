"""Generador de datos sintéticos y simulados para Green Services (EstudIA - Capa 2).

Permite crear desde cero conjuntos de datos reproducibles y realistas de:
- Clientes
- Productos y Catálogo
- Tasa Representativa del Mercado (TRM)
- Transacciones de Ventas (con recurrencia y estacionalidad)
- Compras a Proveedores
- Base Instalada y Coberturas
- Conjuntos con incidencias para pruebas de calidad
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

SECTORES = ["Tecnología", "Financiero", "Salud", "Comercio", "Manufactura", "Educación", "Logística"]
CIUDADES = ["Medellín", "Bogotá", "Cali", "Barranquilla", "Bucaramanga", "Pereira", "Cartagena"]
CANALES = ["Portal Web", "Ejecutivo Comercial", "Correo Electrónico", "WhatsApp Corporativo"]

FAMILIAS_PRODUCTOS = [
    ("PRO01", "Plataforma Cloud Enterprise", "Software Cloud", "Recurrente", "USD", 250.0, 140.0, 12),
    ("PRO02", "Licencia Gestión Documental", "Gestión Información", "Recurrente", "COP", 850000.0, 420000.0, 12),
    ("PRO03", "Módulo Auditoría y Trazabilidad", "Ciberseguridad", "Recurrente", "USD", 180.0, 95.0, 12),
    ("PRO04", "Servicio Backup & Respaldo", "Infraestructura", "Recurrente", "USD", 320.0, 170.0, 12),
    ("PRO05", "Soporte Premium 24/7", "Servicios TI", "Recurrente", "COP", 1200000.0, 600000.0, 12),
    ("PRO06", "Consultoría Migración Datos", "Servicios TI", "Único", "COP", 3500000.0, 1800000.0, 0),
    ("PRO07", "Licencia Firma Electrónica", "Gestión Información", "Recurrente", "USD", 120.0, 60.0, 12),
    ("PRO08", "Paquete Almacenamiento 10TB", "Infraestructura", "Recurrente", "USD", 210.0, 110.0, 12),
    ("PRO09", "Capacitación Operativa IA", "Servicios TI", "Único", "COP", 2200000.0, 1000000.0, 0),
    ("PRO10", "Póliza Mantenimiento Servidores", "Infraestructura", "Recurrente", "COP", 1500000.0, 750000.0, 12)
]

PROVEEDORES = [
    ("PRV01", "Cloud Infrastructure Global LLC"),
    ("PRV02", "Security Softwares International"),
    ("PRV03", "Data Storage & Networks SAS"),
    ("PRV04", "Integradores Tecnológicos Andinos"),
    ("PRV05", "Soluciones de Gestión & Backup SA")
]

class GeneradorDatosSinteticos:
    """Motor de generación y simulación de datos operacionales."""

    def __init__(self, seed: int = 212026):
        self.seed = seed
        random.seed(seed)

    def generar_clientes(self, n: int = 120) -> List[Dict[str, Any]]:
        """Genera listado maestro de clientes con fechas de inicio entre enero y agosto de 2025."""
        clientes = []
        fecha_base = date(2025, 1, 10)
        for i in range(1, n + 1):
            dias_alta = random.randint(0, 240)
            fecha_alta = fecha_base + timedelta(days=dias_alta)
            cid = f"CLI{i:03d}"
            clientes.append({
                "cliente_id": cid,
                "nombre_prueba": f"Cliente Corporativo {i:03d} SAS",
                "sector_prueba": random.choice(SECTORES),
                "ciudad_prueba": random.choice(CIUDADES),
                "fecha_alta": str(fecha_alta),
                "canal_preferido_prueba": random.choice(CANALES),
                "origen_datos": "Generación sintética reproducible"
            })
        return clientes

    def generar_productos(self) -> List[Dict[str, Any]]:
        """Genera el catálogo de productos y servicios."""
        productos = []
        for pid, nombre, fam, tipo, moneda, precio, costo, vig in FAMILIAS_PRODUCTOS:
            productos.append({
                "producto_id": pid,
                "nombre_prueba": nombre,
                "familia_prueba": fam,
                "tipo_prueba": tipo,
                "moneda_lista": moneda,
                "precio_lista": precio,
                "costo_referencia": costo,
                "vigencia_meses": vig,
                "origen_datos": "Generación sintética reproducible"
            })
        return productos

    def generar_proveedores(self) -> List[Dict[str, Any]]:
        """Genera los proveedores de insumos tecnológicos."""
        return [
            {"proveedor_id": pid, "nombre_prueba": nom, "origen_datos": "Generación sintética"}
            for pid, nom in PROVEEDORES
        ]

    def generar_trm(self, fecha_inicio: date = date(2025, 1, 1), fecha_fin: date = date(2026, 10, 31),
                    trm_inicial: float = 4050.0) -> List[Dict[str, Any]]:
        """Genera serie de TRM diaria con paseo aleatorio suave y reversión a la media."""
        serie = []
        actual = trm_inicial
        cur = fecha_inicio
        while cur <= fecha_fin:
            # Variación diaria suave
            shock = random.gauss(0, 18.0)
            pull = (4150.0 - actual) * 0.02
            actual = max(3700.0, min(4500.0, actual + shock + pull))
            serie.append({
                "fecha": str(cur),
                "cop_por_usd": round(actual, 2),
                "origen": "Serie didáctica de prueba no oficial"
            })
            cur += timedelta(days=1)
        return serie

    def generar_ventas(self, clientes: List[Dict[str, Any]], productos: List[Dict[str, Any]],
                       fecha_inicio: date = date(2025, 1, 15), fecha_fin: date = date(2026, 10, 31),
                       total_ventas: int = 1400) -> List[Dict[str, Any]]:
        """Genera transacciones de venta con recurrencia realista y clientes de distintos perfiles."""
        ventas = []
        prod_map = {p["producto_id"]: p for p in productos}
        
        # Asignar peso/afinidad a cada cliente (frecuentes vs ocasionales)
        pesos_clientes = [random.choice([1, 2, 4, 8, 12]) for _ in clientes]
        
        for v_num in range(1, total_ventas + 1):
            c = random.choices(clientes, weights=pesos_clientes, k=1)[0]
            f_alta = date.fromisoformat(c["fecha_alta"])
            dias_disp = (fecha_fin - f_alta).days
            if dias_disp <= 0:
                f_venta = f_alta
            else:
                f_venta = f_alta + timedelta(days=random.randint(0, dias_disp))

            prod = random.choice(productos)
            cantidad = random.choices([1, 2, 3, 5, 10], weights=[50, 30, 12, 6, 2])[0]
            precio_base = float(prod["precio_lista"])
            # Posible descuento por volumen
            descuento = 0.0
            if cantidad >= 5:
                descuento = random.choice([5.0, 10.0])

            # 2.5% probabilidad de anulación
            estado = "Anulada" if random.random() < 0.025 else "Confirmada"

            ventas.append({
                "venta_id": f"VEN{v_num:05d}",
                "fecha": str(f_venta),
                "cliente_id": c["cliente_id"],
                "producto_id": prod["producto_id"],
                "cantidad": cantidad,
                "moneda": prod["moneda_lista"],
                "precio_unitario": precio_base,
                "descuento_pct": descuento,
                "estado": estado,
                "origen_datos": "Generación sintética reproducible"
            })

        # Ordenar cronológicamente
        ventas.sort(key=lambda x: x["fecha"])
        return ventas

    def generar_base_instalada(self, clientes: List[Dict[str, Any]], productos: List[Dict[str, Any]],
                               n_instalaciones: int = 240) -> List[Dict[str, Any]]:
        """Genera contratos y coberturas de servicios activos o vencidos."""
        instalaciones = []
        recurrentes = [p for p in productos if p["tipo_prueba"] == "Recurrente"]
        
        for i in range(1, n_instalaciones + 1):
            c = random.choice(clientes)
            p = random.choice(recurrentes)
            f_alta = date.fromisoformat(c["fecha_alta"])
            dias_desplazamiento = random.randint(0, 360)
            f_inicio = f_alta + timedelta(days=dias_desplazamiento)
            vig_meses = int(p["vigencia_meses"]) or 12
            f_fin = f_inicio + timedelta(days=vig_meses * 30)

            instalaciones.append({
                "instalacion_id": f"INS{i:04d}",
                "cliente_id": c["cliente_id"],
                "producto_id": p["producto_id"],
                "fecha_inicio": str(f_inicio),
                "fecha_fin": str(f_fin),
                "unidades": random.randint(1, 5),
                "origen_datos": "Generación sintética reproducible"
            })
        return instalaciones

    def generar_compras(self, proveedores: List[Dict[str, Any]], productos: List[Dict[str, Any]],
                         n_compras: int = 240) -> List[Dict[str, Any]]:
        """Genera órdenes de compra a proveedores mayoristas."""
        compras = []
        fecha_cur = date(2025, 1, 15)
        for i in range(1, n_compras + 1):
            prv = random.choice(proveedores)
            prod = random.choice(productos)
            fecha_cur += timedelta(days=random.randint(1, 3))
            if fecha_cur > date(2026, 10, 31):
                fecha_cur = date(2026, 10, 31)

            compras.append({
                "compra_id": f"COM{i:04d}",
                "fecha": str(fecha_cur),
                "proveedor_id": prv["proveedor_id"],
                "producto_id": prod["producto_id"],
                "cantidad": random.randint(5, 30),
                "moneda": prod["moneda_lista"],
                "costo_unitario": float(prod["costo_referencia"]),
                "origen_datos": "Generación sintética reproducible"
            })
        return compras

    def guardar_dataset_completo(self, output_dir: Path) -> Dict[str, int]:
        """Ejecuta la generación completa y persiste los CSVs en el directorio destino."""
        output_dir.mkdir(parents=True, exist_ok=True)

        clientes = self.generar_clientes(120)
        productos = self.generar_productos()
        proveedores = self.generar_proveedores()
        trm = self.generar_trm()
        ventas = self.generar_ventas(clientes, productos, total_ventas=1407)
        base_instalada = self.generar_base_instalada(clientes, productos, 243)
        compras = self.generar_compras(proveedores, productos, 240)

        tablas = {
            "clientes.csv": clientes,
            "productos.csv": productos,
            "proveedores.csv": proveedores,
            "trm_prueba.csv": trm,
            "ventas.csv": ventas,
            "base_instalada.csv": base_instalada,
            "compras.csv": compras
        }

        conteo = {}
        for fname, data in tablas.items():
            fpath = output_dir / fname
            with open(fpath, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
                writer.writeheader()
                writer.writerows(data)
            conteo[fname] = len(data)

        return conteo
