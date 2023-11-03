from silk_road import db, create_app
from silk_road.models import *
app = create_app()

r = Category(name="closes")
with app.app_context():
    db.session.add(r)
    db.session.commit()

r = Category(name="plates")
with app.app_context():
    db.session.add(r)
    db.session.commit()


p = Product(
        name="shirt",
        material="cutton",
        description="this is shirt",
        care="washed +25",
        condition="new",
        design="ef",
        price=123,
        old_price=456,
        category_id=1
)
with app.app_context():
    db.session.add(p)
    db.session.commit()


# r = Photo(base="photo", product_id=1)
# with app.app_context():
#     db.session.add(r)
#     db.session.commit()

# r = Color(name="white", product_id=1)
# with app.app_context():
#     db.session.add(r)
#     db.session.commit()

# r = Size(deminsion="41", product_id=1)
# with app.app_context():
#     db.session.add(r)
#     db.session.commit()

# r = Weight(deminsion="4", product_id=1)
# with app.app_context():
#     db.session.add(r)
#     db.session.commit()






# photo="data:image/jpeg;base64,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",