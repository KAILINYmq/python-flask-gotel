# coding: utf-8
from agile.database import AuditModel
from agile.extensions import db

BRAND_CATEGORY = [
    ('chaoneng', 'HC'),
    ('omo', 'HC'),
    ('comfort', 'HC'),
    ('dove', 'PW'),
    ('downy', 'HC'),
    ('febreze', 'HC'),
    ('folicure', 'PW'),
    ('lhp', 'HC'),
    ('lux', 'PW'),
    ('ogx', 'PC'),
    ('clear', 'PC'),
    ('clear', 'PW'),
    ('phyto', 'PC'),
    ('tresemme', 'PC'),
    ('mangum', 'RE'),
]

ALL_BRAND = [
    ('Chaoneng01', 'brand_Chaoneng01.png', 'chaoneng'),
    ('OMO01', 'brand_OMO01.png', 'omo'),
    ('OMO02', 'brand_OMO02.png', 'omo'),
    ('OMO03', 'brand_OMO03.png', 'omo'),
    ('Clear01', 'brand_Clear01.png', 'clear'),
    ('Comfort01', 'brand_Comfort01.png', 'comfort'),
    ('Comfort02', 'brand_Comfort02.png', 'comfort'),
    ('Dove01', 'brand_Dove01.png', 'dove'),
    ('Dove02', 'brand_Dove02.png', 'dove'),
    ('Dove03', 'brand_Dove03.png', 'dove'),
    ('Dove04', 'brand_Dove04.png', 'dove'),
    ('Dove05', 'brand_Dove05.png', 'dove'),
    ('Dove06', 'brand_Dove06.png', 'dove'),
    ('Dove07', 'brand_Dove07.png', 'dove'),
    ('Dove08', 'brand_Dove08.png', 'dove'),
    ('Dove09', 'brand_Dove09.png', 'dove'),
    ('Downy01', 'brand_Downy01.png', 'downy'),
    ('Febreze01', 'brand_Febreze01.png', 'febreze'),
    ('FOLICURE01', 'brand_FOLICURE01.png', 'folicure'),
    ('FOLICURE02', 'brand_FOLICURE02.png', 'folicure'),
    ('LHP01', 'brand_LHP01.png', 'lhp'),
    ('LHP02', 'brand_LHP02.png', 'lhp'),
    ('LHP03', 'brand_LHP03.png', 'lhp'),
    ('LHP04', 'brand_LHP04.png', 'lhp'),
    ('LHP05', 'brand_LHP05.png', 'lhp'),
    ('LHP06', 'brand_LHP06.png', 'lhp'),
    ('LHP07', 'brand_LHP07.png', 'lhp'),
    ('LHP08', 'brand_LHP08.png', 'lhp'),
    ('Lux01', 'brand_Lux01.png', 'lux'),
    ('Lux02', 'brand_Lux02.png', 'lux'),
    ('Lux03', 'brand_Lux03.png', 'lux'),
    ('Lux04', 'brand_Lux04.png', 'lux'),
    ('Ogx01', 'brand_Ogx01.png', 'ogx'),
    ('PHYTO01', 'brand_PHYTO01.png', 'phyto'),
    ('TRESemme01', 'brand_TRESemme01.png', 'tresemme'),
    ('TRESemme02', 'brand_TRESemme02.png', 'tresemme'),
    ('MAGNUM01', 'brand_MAGNUM01.png', 'mangum'),
    ('MAGNUM02', 'brand_MAGNUM02.png', 'mangum'),
]

ALL_PACKING = [
    ('OMO-Package01', 'OMO-Package01.png', 'omo'),
    ('OMO-Package02', 'OMO-Package02.png', 'omo'),
    ('OMO-Package03', 'OMO-Package03.png', 'omo'),
    ('OMO-Package04', 'OMO-Package04.png', 'omo'),
    ('Comfort-Package01', 'Comfort-Package01.png', 'comfort'),
    ('Comfort-Package02', 'Comfort-Package02.png', 'comfort'),
    ('Comfort-Package03', 'Comfort-Package03.png', 'comfort'),
    ('Comfort-Package04', 'Comfort-Package04.png', 'comfort'),
    ('Comfort-Package05', 'Comfort-Package05.png', 'comfort'),
    ('Comfort-Package06', 'Comfort-Package06.png', 'comfort'),
    ('Comfort-Package07', 'Comfort-Package07.png', 'comfort'),
    ('Comfort-Package08', 'Comfort-Package08.png', 'comfort'),
    ('Comfort-Package09', 'Comfort-Package09.png', 'comfort'),
    ('Downy-Package01', 'Downy-Package01.png', 'downy'),
    ('Downy-Package02', 'Downy-Package02.png', 'downy'),
    ('Chaoneng-Package01', 'Chaoneng-Package01.png', 'chaoneng'),
    ('Chaoneng-Package02', 'Chaoneng-Package02.png', 'chaoneng'),
    ('Clear-Package01', 'Clear-Package01.png', 'clear'),
    ('Dove-Package01', 'Dove-Package01.png', 'dove'),
    ('Dove-Package02', 'Dove-Package02.png', 'dove'),
    ('Dove-Package03', 'Dove-Package03.png', 'dove'),
    ('Dove-Package04', 'Dove-Package04.png', 'dove'),
    ('Dove-Package05', 'Dove-Package05.png', 'dove'),
    ('Dove-Package06', 'Dove-Package06.png', 'dove'),
    ('Dove-Package07', 'Dove-Package07.png', 'dove'),
    ('Dove-Package08', 'Dove-Package08.png', 'dove'),
    ('Dove-Package09', 'Dove-Package09.png', 'dove'),
    ('Dove-Package10', 'Dove-Package10.png', 'dove'),
    ('Dove-Package11', 'Dove-Package11.png', 'dove'),
    ('Dove-Package12', 'Dove-Package12.png', 'dove'),
    ('Dove-Package13', 'Dove-Package13.png', 'dove'),
    ('Dove-Package14', 'Dove-Package14.png', 'dove'),
    ('Dove-Package15', 'Dove-Package15.png', 'dove'),
    ('Dove-Package16', 'Dove-Package16.png', 'dove'),
    ('Dove-Package17', 'Dove-Package17.png', 'dove'),
    ('Dove-Package18', 'Dove-Package18.png', 'dove'),
    ('Dove-Package19', 'Dove-Package19.png', 'dove'),
    ('Dove-Package20', 'Dove-Package20.png', 'dove'),
    ('Dove-Package21', 'Dove-Package21.png', 'dove'),
    ('Dove-Package22', 'Dove-Package22.png', 'dove'),
    ('Dove-Package23', 'Dove-Package23.png', 'dove'),
    ('Dove-Package24', 'Dove-Package24.png', 'dove'),
    ('Dove-Package25', 'Dove-Package25.png', 'dove'),
    ('Dove-Package26', 'Dove-Package26.png', 'dove'),
    ('Dove-Package27', 'Dove-Package27.png', 'dove'),
    ('Dove-Package28', 'Dove-Package28.png', 'dove'),
    ('Dove-Package29', 'Dove-Package29.png', 'dove'),
    ('Dove-Package30', 'Dove-Package30.png', 'dove'),
    ('Dove-Package31', 'Dove-Package31.png', 'dove'),
    ('Dove-Package32', 'Dove-Package32.png', 'dove'),
    ('Dove-Package33', 'Dove-Package33.png', 'dove'),
    ('Dove-Package34', 'Dove-Package34.png', 'dove'),
    ('Dove-Package35', 'Dove-Package35.png', 'dove'),
    ('Dove-Package36', 'Dove-Package36.png', 'dove'),
    ('Dove-Package37', 'Dove-Package37.png', 'dove'),
    ('Dove-Package38', 'Dove-Package38.png', 'dove'),
    ('Dove-Package39', 'Dove-Package39.png', 'dove'),
    ('Dove-Package40', 'Dove-Package40.png', 'dove'),
    ('Dove-Package41', 'Dove-Package41.png', 'dove'),
    ('Dove-Package42', 'Dove-Package42.png', 'dove'),
    ('Dove-Package43', 'Dove-Package43.png', 'dove'),
    ('Dove-Package44', 'Dove-Package44.png', 'dove'),
    ('Febreze-Package01', 'Febreze-Package01.png', 'febreze'),
    ('Febreze-Package02', 'Febreze-Package02.png', 'febreze'),
    ('FOLICURE-Package01', 'FOLICURE-Package01.png', 'folicure'),
    ('FOLICURE-Package02', 'FOLICURE-Package02.png', 'folicure'),
    ('FOLICURE-Package03', 'FOLICURE-Package03.png', 'folicure'),
    ('FOLICURE-Package04', 'FOLICURE-Package04.png', 'folicure'),
    ('FOLICURE-Package05', 'FOLICURE-Package05.png', 'folicure'),
    ('FOLICURE-Package06', 'FOLICURE-Package06.png', 'folicure'),
    ('FOLICURE-Package07', 'FOLICURE-Package07.png', 'folicure'),
    ('FOLICURE-Package08', 'FOLICURE-Package08.png', 'folicure'),
    ('LHP-Package01', 'LHP-Package01.png', 'lhp'),
    ('LHP-Package02', 'LHP-Package02.png', 'lhp'),
    ('LHP-Package03', 'LHP-Package03.png', 'lhp'),
    ('LHP-Package04', 'LHP-Package04.png', 'lhp'),
    ('LHP-Package05', 'LHP-Package05.png', 'lhp'),
    ('LHP-Package06', 'LHP-Package06.png', 'lhp'),
    ('LHP-Package07', 'LHP-Package07.png', 'lhp'),
    ('LHP-Package08', 'LHP-Package08.png', 'lhp'),
    ('Lux-Package01', 'Lux-Package01.png', 'lux'),
    ('Lux-Package02', 'Lux-Package02.png', 'lux'),
    ('Lux-Package03', 'Lux-Package03.png', 'lux'),
    ('Lux-Package04', 'Lux-Package04.png', 'lux'),
    ('Lux-Package05', 'Lux-Package05.png', 'lux'),
    ('Lux-Package06', 'Lux-Package06.png', 'lux'),
    ('Lux-Package07', 'Lux-Package07.png', 'lux'),
    ('Ogx-Package01', 'Ogx-Package01.png', 'ogx'),
    ('Ogx-Package02', 'Ogx-Package02.png', 'ogx'),
    ('Ogx-Package03', 'Ogx-Package03.png', 'ogx'),
    ('Ogx-Package04', 'Ogx-Package04.png', 'ogx'),
    ('Ogx-Package05', 'Ogx-Package05.png', 'ogx'),
    ('Ogx-Package06', 'Ogx-Package06.png', 'ogx'),
    ('Ogx-Package07', 'Ogx-Package07.png', 'ogx'),
    ('Ogx-Package08', 'Ogx-Package08.png', 'ogx'),
    ('Ogx-Package09', 'Ogx-Package09.png', 'ogx'),
    ('Ogx-Package10', 'Ogx-Package10.png', 'ogx'),
    ('Ogx-Package11', 'Ogx-Package11.png', 'ogx'),
    ('Ogx-Package12', 'Ogx-Package12.png', 'ogx'),
    ('Ogx-Package13', 'Ogx-Package13.png', 'ogx'),
    ('Ogx-Package14', 'Ogx-Package14.png', 'ogx'),
    ('Ogx-Package15', 'Ogx-Package15.png', 'ogx'),
    ('PHYTO-Package01', 'PHYTO-Package01.png', 'phyto'),
    ('TRESemme-Package01', 'TRESemme-Package01.png', 'tresemme'),
    ('TRESemme-Package02', 'TRESemme-Package02.png', 'tresemme'),
    ('TRESemme-Package03', 'TRESemme-Package03.png', 'tresemme'),
    ('TRESemme-Package04', 'TRESemme-Package04.png', 'tresemme'),
    ('TRESemme-Package05', 'TRESemme-Package05.png', 'tresemme'),
    ('TRESemme-Package06', 'TRESemme-Package06.png', 'tresemme'),
    ('TRESemme-Package07', 'TRESemme-Package07.png', 'tresemme'),
    ('TRESemme-Package08', 'TRESemme-Package08.png', 'tresemme'),
    ('TRESemme-Package09', 'TRESemme-Package09.png', 'tresemme'),
    ('TRESemme-Package10', 'TRESemme-Package10.png', 'tresemme'),
    ('TRESemme-Package11', 'TRESemme-Package11.png', 'tresemme'),
    ('TRESemme-Package12', 'TRESemme-Package12.png', 'tresemme'),
    ('TRESemme-Package13', 'TRESemme-Package13.png', 'tresemme'),
    ('TRESemme-Package14', 'TRESemme-Package14.png', 'tresemme'),
    ('TRESemme-Package15', 'TRESemme-Package15.png', 'tresemme'),
    ('TRESemme-Package16', 'TRESemme-Package16.png', 'tresemme'),
    ('TRESemme-Package17', 'TRESemme-Package17.png', 'tresemme'),
    ('TRESemme-Package18', 'TRESemme-Package18.png', 'tresemme'),
    ('TRESemme-Package19', 'TRESemme-Package19.png', 'tresemme'),
    ('TRESemme-Package20', 'TRESemme-Package20.png', 'tresemme'),
    ('TRESemme-Package21', 'TRESemme-Package21.png', 'tresemme'),
    ('MAGNUM-Package01', 'MAGNUM-Package01.png', 'mangum')
]

ALL_BACKGROUND = [
    ('OMO01', 'bg_OMO01.png', 'omo'),
    ('Chaoneng01', 'bg_Chaoneng01.png', 'chaoneng'),
    ('Chaoneng02', 'bg_Chaoneng02.png', 'chaoneng'),
    ('Comfort01', 'bg_Comfort01.png', 'comfort'),
    ('Comfort02', 'bg_Comfort02.png', 'comfort'),
    ('Comfort03', 'bg_Comfort03.png', 'comfort'),
    ('Comfort04', 'bg_Comfort04.png', 'comfort'),
    ('Comfort05', 'bg_Comfort05.png', 'comfort'),
    ('Comfort06', 'bg_Comfort06.png', 'comfort'),
    ('Comfort07', 'bg_Comfort07.png', 'comfort'),
    ('Comfort08', 'bg_Comfort08.png', 'comfort'),
    ('Comfort09', 'bg_Comfort09.png', 'comfort'),
    ('Comfort10', 'bg_Comfort10.png', 'comfort'),
    ('Comfort11', 'bg_Comfort11.png', 'comfort'),
    ('Comfort12', 'bg_Comfort12.png', 'comfort'),
    ('Dove01', 'bg_Dove01.png', 'dove'),
    ('Dove02', 'bg_Dove02.png', 'dove'),
    ('Dove03', 'bg_Dove03.png', 'dove'),
    ('Dove04', 'bg_Dove04.png', 'dove'),
    ('Dove05', 'bg_Dove05.png', 'dove'),
    ('Dove06', 'bg_Dove06.png', 'dove'),
    ('Dove07', 'bg_Dove07.png', 'dove'),
    ('Dove08', 'bg_Dove08.png', 'dove'),
    ('Dove09', 'bg_Dove09.png', 'dove'),
    ('Dove10', 'bg_Dove10.png', 'dove'),
    ('Dove11', 'bg_Dove11.png', 'dove'),
    ('Downy01', 'bg_Downy01.png', 'downy'),
    ('Febreze01', 'bg_Febreze01.png', 'febreze'),
    ('FOLICURE01', 'bg_FOLICURE01.png', 'folicure'),
    ('FOLICURE02', 'bg_FOLICURE02.png', 'folicure'),
    ('LHP01', 'bg_LHP01.png', 'lhp'),
    ('LHP02', 'bg_LHP02.png', 'lhp'),
    ('LHP03', 'bg_LHP03.png', 'lhp'),
    ('LHP04', 'bg_LHP04.png', 'lhp'),
    ('Lux01', 'bg_Lux01.png', 'lux'),
    ('Lux02', 'bg_Lux02.png', 'lux'),
    ('Lux03', 'bg_Lux03.png', 'lux'),
    ('Lux04', 'bg_Lux04.png', 'lux'),
    ('Lux05', 'bg_Lux05.png', 'lux'),
    ('MAGNUM01', 'bg_MAGNUM01.png', 'mangum'),
    ('MAGNUM02', 'bg_MAGNUM02.png', 'mangum'),
    ('MAGNUM03', 'bg_MAGNUM03.png', 'mangum'),
    ('MAGNUM04', 'bg_MAGNUM04.png', 'mangum')
]


class Brand(AuditModel):
    """
        品牌图
    """
    id = db.Column(db.Integer, primary_key=True)
    # image name, ensure unique
    name = db.Column(db.String(164))
    # brand code
    code = db.Column(db.String(10))
    location = db.Column(db.String(300))

    @staticmethod
    def init_brand():
        for _name, _location, _code in ALL_BRAND:
            brand = Brand.query.filter_by(name=_name).first()
            if brand is None:
                brand = Brand(name=_name, location=_location, code=_code, created_by_fk=1, updated_by_fk=1)
            db.session.add(brand)
        db.session.commit()
        print('brand init success')


class Packing(AuditModel):
    """
        包装图
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(164))
    location = db.Column(db.String(300))
    brandCode = db.Column(db.String(10))

    @staticmethod
    def init_packing():
        for _name, _location, _code in ALL_PACKING:
            packing = Packing.query.filter_by(name=_name).first()
            if packing is None:
                packing = Packing(name=_name, location=_location, brandCode=_code, created_by_fk=1, updated_by_fk=1)
            db.session.add(packing)
        db.session.commit()
        print('packing init success')


class Background(AuditModel):
    """
        背景图
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(164))
    location = db.Column(db.String(300))
    brandCode = db.Column(db.String(10))

    @staticmethod
    def init_background():
        for _name, _location, _code in ALL_BACKGROUND:
            background = Background.query.filter_by(name=_name).first()
            if background is None:
                background = Background(name=_name, location=_location, brandCode=_code, created_by_fk=1,
                                        updated_by_fk=1)
            else:
                background.brandCode = _code
            db.session.add(background)
        db.session.commit()
        print('background init success')
