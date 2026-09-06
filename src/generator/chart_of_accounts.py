"""
Plan de Cuentas Contable (Chart of Accounts - COA) y Plantillas de Transacción
Normativa IFRS / NIIF para Empresa Multinacional de Tecnología y Servicios.
"""

ENTITIES = [
    {
        "entity_id": "ENT-01",
        "entity_name": "Apex Global Corp (HQ)",
        "country": "United States",
        "currency": "USD",
        "weight": 0.45
    },
    {
        "entity_id": "ENT-02",
        "entity_name": "Apex Iberia Logistics S.L.",
        "country": "Spain",
        "currency": "EUR",
        "weight": 0.25
    },
    {
        "entity_id": "ENT-03",
        "entity_name": "Apex Andina Soluciones S.A.S.",
        "country": "Colombia",
        "currency": "COP",
        "weight": 0.18
    },
    {
        "entity_id": "ENT-04",
        "entity_name": "Apex Operaciones del Caribe C.A.",
        "country": "Venezuela",
        "currency": "VES",
        "weight": 0.12
    }
]

COST_CENTERS = [
    {"cost_center_id": "CC-100", "cost_center_name": "Finanzas & Contabilidad Corporativa"},
    {"cost_center_id": "CC-200", "cost_center_name": "Ventas & Growth Marketing"},
    {"cost_center_id": "CC-300", "cost_center_name": "Operaciones & Soporte de Clientes"},
    {"cost_center_id": "CC-400", "cost_center_name": "Ingeniería de Software & Cloud Platform"},
    {"cost_center_id": "CC-500", "cost_center_name": "Recursos Humanos & Talento"}
]

CHART_OF_ACCOUNTS = [
    # --- ACTIVOS (1.x) ---
    {
        "account_code": "1.1.01.01",
        "account_name": "Caja Chica y Fondos Fijos",
        "statement": "BALANCE_SHEET",
        "financial_class": "ACTIVO",
        "subclass": "ACTIVO_CORRIENTE",
        "normal_balance": "DEBIT"
    },
    {
        "account_code": "1.1.02.01",
        "account_name": "Banco Operativo Principal",
        "statement": "BALANCE_SHEET",
        "financial_class": "ACTIVO",
        "subclass": "ACTIVO_CORRIENTE",
        "normal_balance": "DEBIT"
    },
    {
        "account_code": "1.1.03.01",
        "account_name": "Cuentas por Cobrar Comerciales",
        "statement": "BALANCE_SHEET",
        "financial_class": "ACTIVO",
        "subclass": "ACTIVO_CORRIENTE",
        "normal_balance": "DEBIT"
    },
    {
        "account_code": "1.1.04.01",
        "account_name": "Inventario de Servidores y Equipos",
        "statement": "BALANCE_SHEET",
        "financial_class": "ACTIVO",
        "subclass": "ACTIVO_CORRIENTE",
        "normal_balance": "DEBIT"
    },
    {
        "account_code": "1.2.01.01",
        "account_name": "Propiedad, Planta y Equipos de Cómputo",
        "statement": "BALANCE_SHEET",
        "financial_class": "ACTIVO",
        "subclass": "ACTIVO_NO_CORRIENTE",
        "normal_balance": "DEBIT"
    },
    {
        "account_code": "1.2.02.01",
        "account_name": "Depreciación Acumulada de Equipos",
        "statement": "BALANCE_SHEET",
        "financial_class": "ACTIVO",
        "subclass": "ACTIVO_NO_CORRIENTE",
        "normal_balance": "CREDIT"
    },

    # --- PASIVOS (2.x) ---
    {
        "account_code": "2.1.01.01",
        "account_name": "Cuentas por Pagar Proveedores",
        "statement": "BALANCE_SHEET",
        "financial_class": "PASIVO",
        "subclass": "PASIVO_CORRIENTE",
        "normal_balance": "CREDIT"
    },
    {
        "account_code": "2.1.02.01",
        "account_name": "Retenciones e Impuestos por Pagar",
        "statement": "BALANCE_SHEET",
        "financial_class": "PASIVO",
        "subclass": "PASIVO_CORRIENTE",
        "normal_balance": "CREDIT"
    },
    {
        "account_code": "2.1.03.01",
        "account_name": "Préstamos y Líneas de Crédito Bancario",
        "statement": "BALANCE_SHEET",
        "financial_class": "PASIVO",
        "subclass": "PASIVO_CORRIENTE",
        "normal_balance": "CREDIT"
    },
    {
        "account_code": "2.2.01.01",
        "account_name": "Deuda Corporativa a Largo Plazo",
        "statement": "BALANCE_SHEET",
        "financial_class": "PASIVO",
        "subclass": "PASIVO_NO_CORRIENTE",
        "normal_balance": "CREDIT"
    },

    # --- PATRIMONIO (3.x) ---
    {
        "account_code": "3.1.01.01",
        "account_name": "Capital Social Autorizado",
        "statement": "BALANCE_SHEET",
        "financial_class": "PATRIMONIO",
        "subclass": "CAPITAL",
        "normal_balance": "CREDIT"
    },
    {
        "account_code": "3.2.01.01",
        "account_name": "Resultados Acumulados de Ejercicios Anteriores",
        "statement": "BALANCE_SHEET",
        "financial_class": "PATRIMONIO",
        "subclass": "RESERVAS_Y_RESULTADOS",
        "normal_balance": "CREDIT"
    },

    # --- INGRESOS (4.x) ---
    {
        "account_code": "4.1.01.01",
        "account_name": "Ingresos por Suscripciones SaaS y Licencias",
        "statement": "INCOME_STATEMENT",
        "financial_class": "INGRESOS",
        "subclass": "INGRESOS_OPERACIONALES",
        "normal_balance": "CREDIT"
    },
    {
        "account_code": "4.1.02.01",
        "account_name": "Ingresos por Servicios de Consultoría e Implementación",
        "statement": "INCOME_STATEMENT",
        "financial_class": "INGRESOS",
        "subclass": "INGRESOS_OPERACIONALES",
        "normal_balance": "CREDIT"
    },
    {
        "account_code": "4.2.01.01",
        "account_name": "Ingresos Financieros y Rendimientos",
        "statement": "INCOME_STATEMENT",
        "financial_class": "INGRESOS",
        "subclass": "OTROS_INGRESOS",
        "normal_balance": "CREDIT"
    },

    # --- COSTOS (5.x) ---
    {
        "account_code": "5.1.01.01",
        "account_name": "Costo de Ventas - Infraestructura de Entrega",
        "statement": "INCOME_STATEMENT",
        "financial_class": "COSTOS",
        "subclass": "COSTO_DE_VENTAS",
        "normal_balance": "DEBIT"
    },
    {
        "account_code": "5.1.02.01",
        "account_name": "Costo de Equipos Vendidos / Hardware",
        "statement": "INCOME_STATEMENT",
        "financial_class": "COSTOS",
        "subclass": "COSTO_DE_VENTAS",
        "normal_balance": "DEBIT"
    },

    # --- GASTOS OPERATIVOS (6.x) ---
    {
        "account_code": "6.1.01.01",
        "account_name": "Gastos de Salarios y Prestaciones de Personal",
        "statement": "INCOME_STATEMENT",
        "financial_class": "GASTOS",
        "subclass": "GASTOS_ADMINISTRATIVOS",
        "normal_balance": "DEBIT"
    },
    {
        "account_code": "6.1.02.01",
        "account_name": "Gastos de Alquiler de Oficinas y Co-Working",
        "statement": "INCOME_STATEMENT",
        "financial_class": "GASTOS",
        "subclass": "GASTOS_ADMINISTRATIVOS",
        "normal_balance": "DEBIT"
    },
    {
        "account_code": "6.1.03.01",
        "account_name": "Gasto de Depreciación y Amortización",
        "statement": "INCOME_STATEMENT",
        "financial_class": "GASTOS",
        "subclass": "GASTOS_ADMINISTRATIVOS",
        "normal_balance": "DEBIT"
    },
    {
        "account_code": "6.2.01.01",
        "account_name": "Gastos de Publicidad, Pauta Digital y Eventos",
        "statement": "INCOME_STATEMENT",
        "financial_class": "GASTOS",
        "subclass": "GASTOS_VENTAS_MARKETING",
        "normal_balance": "DEBIT"
    },
    {
        "account_code": "6.3.01.01",
        "account_name": "Gastos de Infraestructura Cloud (AWS, Databricks, Snowflake)",
        "statement": "INCOME_STATEMENT",
        "financial_class": "GASTOS",
        "subclass": "GASTOS_TECNOLOGIA_ID",
        "normal_balance": "DEBIT"
    },
    {
        "account_code": "6.4.01.01",
        "account_name": "Gastos Financieros, Comisiones y Diferencial Cambiario",
        "statement": "INCOME_STATEMENT",
        "financial_class": "GASTOS",
        "subclass": "GASTOS_FINANCIEROS",
        "normal_balance": "DEBIT"
    }
]

TRANSACTION_TEMPLATES = [
    {
        "event_type": "VENTA_SUBSCRIPCION_CREDITO",
        "description_prefix": "Facturación suscripción anual SaaS cliente",
        "cost_center_id": "CC-200",
        "weight": 0.22,
        "amount_range_usd": (1500, 45000),
        "lines": [
            {"account_code": "1.1.03.01", "entry_type": "DEBIT", "ratio": 1.0},
            {"account_code": "4.1.01.01", "entry_type": "CREDIT", "ratio": 1.0}
        ]
    },
    {
        "event_type": "COBRO_CLIENTE_BANCO",
        "description_prefix": "Liquidación y cobro de factura por transferencia",
        "cost_center_id": "CC-100",
        "weight": 0.20,
        "amount_range_usd": (1500, 45000),
        "lines": [
            {"account_code": "1.1.02.01", "entry_type": "DEBIT", "ratio": 1.0},
            {"account_code": "1.1.03.01", "entry_type": "CREDIT", "ratio": 1.0}
        ]
    },
    {
        "event_type": "VENTA_CONSULTORIA_CONTADO",
        "description_prefix": "Servicios profesionales de ingeniería y datos",
        "cost_center_id": "CC-400",
        "weight": 0.10,
        "amount_range_usd": (3000, 25000),
        "lines": [
            {"account_code": "1.1.02.01", "entry_type": "DEBIT", "ratio": 1.0},
            {"account_code": "4.1.02.01", "entry_type": "CREDIT", "ratio": 1.0}
        ]
    },
    {
        "event_type": "COMPRA_EQUIPAMIENTO_PROVEEDOR",
        "description_prefix": "Adquisición de racks y hardware especializado",
        "cost_center_id": "CC-300",
        "weight": 0.08,
        "amount_range_usd": (5000, 60000),
        "lines": [
            {"account_code": "1.1.04.01", "entry_type": "DEBIT", "ratio": 1.0},
            {"account_code": "2.1.01.01", "entry_type": "CREDIT", "ratio": 1.0}
        ]
    },
    {
        "event_type": "PAGO_FACTURA_PROVEEDOR",
        "description_prefix": "Pago electrónico a proveedor de hardware",
        "cost_center_id": "CC-100",
        "weight": 0.08,
        "amount_range_usd": (5000, 60000),
        "lines": [
            {"account_code": "2.1.01.01", "entry_type": "DEBIT", "ratio": 1.0},
            {"account_code": "1.1.02.01", "entry_type": "CREDIT", "ratio": 1.0}
        ]
    },
    {
        "event_type": "RECONOCIMIENTO_COSTO_VENTA",
        "description_prefix": "Reconocimiento de costo directo por entrega de servicio",
        "cost_center_id": "CC-300",
        "weight": 0.08,
        "amount_range_usd": (1000, 18000),
        "lines": [
            {"account_code": "5.1.01.01", "entry_type": "DEBIT", "ratio": 1.0},
            {"account_code": "1.1.04.01", "entry_type": "CREDIT", "ratio": 1.0}
        ]
    },
    {
        "event_type": "PAGO_NOMINA_QUINCENAL",
        "description_prefix": "Dispersión de nómina y cargas laborales",
        "cost_center_id": "CC-500",
        "weight": 0.09,
        "amount_range_usd": (20000, 150000),
        "lines": [
            {"account_code": "6.1.01.01", "entry_type": "DEBIT", "ratio": 1.0},
            {"account_code": "1.1.02.01", "entry_type": "CREDIT", "ratio": 1.0}
        ]
    },
    {
        "event_type": "GASTO_CLOUD_INFRAESTRUCTURA",
        "description_prefix": "Consumo de clusters Databricks, Snowflake y AWS",
        "cost_center_id": "CC-400",
        "weight": 0.06,
        "amount_range_usd": (4000, 35000),
        "lines": [
            {"account_code": "6.3.01.01", "entry_type": "DEBIT", "ratio": 1.0},
            {"account_code": "1.1.02.01", "entry_type": "CREDIT", "ratio": 1.0}
        ]
    },
    {
        "event_type": "GASTO_MARKETING_DIGITAL",
        "description_prefix": "Inversión en pauta publicitaria SEM y social ads",
        "cost_center_id": "CC-200",
        "weight": 0.04,
        "amount_range_usd": (2000, 20000),
        "lines": [
            {"account_code": "6.2.01.01", "entry_type": "DEBIT", "ratio": 1.0},
            {"account_code": "1.1.02.01", "entry_type": "CREDIT", "ratio": 1.0}
        ]
    },
    {
        "event_type": "GASTO_ALQUILER_HUB",
        "description_prefix": "Cuota mensual de arrendamiento y servicios de oficinas",
        "cost_center_id": "CC-100",
        "weight": 0.02,
        "amount_range_usd": (3000, 15000),
        "lines": [
            {"account_code": "6.1.02.01", "entry_type": "DEBIT", "ratio": 1.0},
            {"account_code": "1.1.02.01", "entry_type": "CREDIT", "ratio": 1.0}
        ]
    },
    {
        "event_type": "DEPRECIACION_ACTIVOS_FIJOS",
        "description_prefix": "Asiento de ajuste mensual por depreciación lineal",
        "cost_center_id": "CC-100",
        "weight": 0.02,
        "amount_range_usd": (1200, 8000),
        "lines": [
            {"account_code": "6.1.03.01", "entry_type": "DEBIT", "ratio": 1.0},
            {"account_code": "1.2.02.01", "entry_type": "CREDIT", "ratio": 1.0}
        ]
    },
    {
        "event_type": "COMISIONES_Y_DIFERENCIAL_CAMBIARIO",
        "description_prefix": "Ajuste por fluctuación cambiaria y gastos bancarios",
        "cost_center_id": "CC-100",
        "weight": 0.01,
        "amount_range_usd": (200, 4000),
        "lines": [
            {"account_code": "6.4.01.01", "entry_type": "DEBIT", "ratio": 1.0},
            {"account_code": "1.1.02.01", "entry_type": "CREDIT", "ratio": 1.0}
        ]
    }
]
