TREND_SOURCE = [('Trend One Pager', 'ONEP'),
                ('China eCommerce', 'CNEC'),
                ('China Social Media', 'CNSM')
                ]
ALL_SOURCES = [item[1] for item in TREND_SOURCE]

CATEGORY_MAP2ECDB = {
    'HCL': 'fab-cln',
    'HCS': 'fab-con',
    'PCS': 'shampoo',
    'PCP': 'postwash',
    'PWS': 'shower-gel',
    'PCO': 'oral',
    'REI': 'icecream'
}

ECDB_MAP2CATEGORY = dict([(each[1], each[0]) for each in CATEGORY_MAP2ECDB.items()])

ATTR_ZH = {
    "benefit-safety": "安全",
    "benefit-cloth_care_during_wash": "无缠绕",
    "benefit-floral_fragrance": "花香",
    "benefit-perfume_fragrance": "果香",
    "benefit-anti-mold": "防霉",
    "benefit-skincare_during_wash": "护肤",
    "benefit-economical": "经济",
    "benefit-anti-static": "除静电",
    "benefit-shape": "护形",
    "benefit-general_fragrance": "香氛",
    "benefit-other_fragrance": "其它香氛",
    "benefit-color_care": "护色",
    "benefit-gentle_as_in_ph": "PH中性",
    "benefit-emotional": "情感",
    "benefit-general_cleansing": "清洁",
    "benefit-anti-moth": "防蛀",
    "benefit-deodorant": "除臭",
    "benefit-sensorial": "感观",
    "benefit-stain_removal": "去渍",
    "benefit-convenient_wash_method": "省时",
    "benefit-care_after_wash": "洗后护衣",
    "benefit-foaming": "泡沬",
    "benefit-volume_saving": "用量少",
    "benefit-energy_saving": "省力",
    "benefit-anti-bacteria": "除菌",
    "benefit-fiber_care": "护衣",
    "benefit-general_care": "多效",
    "benefit-anti-pilling": "防静电",
    "benefit-gentle_to_skin_when_wearing_clothes": "温和",
    "benefit-anti-aging": "除旧",
    "benefit-environmental_friendly": "环保",
    "benefit-anti-mite": "除螨",
    "benefit-softness": "柔软",
    "benefit-plant_fragrance": "木香",
    "benefit-fruit_fragrance": "果香"
}
