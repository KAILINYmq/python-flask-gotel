from flask import request, json
from flask_restplus import Resource

from agile.commons.api_response import ApiResponse, ResposeStatus
from agile.models import Name_table, Type_table, Tag, Guestbook
from agile.extensions import db


class TagList( Resource ):
    """Get all tag"""

    def get(self):
        allName = db.session.query(Tag).all()
        return ApiResponse( [name.label for name in allName], ResposeStatus.Success )

class ActivityName( Resource ):
    """Get all ActivityName"""

    def get(self):
        allName = db.session.query(Name_table).all()
        return ApiResponse( [name.name for name in allName], ResposeStatus.Success )


class ActivityType( Resource ):
    """Get all ActivityType"""

    def get(self):
        allName = db.session.query(Type_table).all()
        return ApiResponse( [name.name for name in allName], ResposeStatus.Success )

class AllList( Resource ):
    """Get all ActivityType"""

    def get(self):
        result = {}
        allName = db.session.query( Name_table ).all()
        result["ActivityName"] = [name.name for name in allName]

        allName = db.session.query(Type_table).all()
        result["ActivityType"] = [name.name for name in allName]

        allName = db.session.query( Tag ).all()
        result["Tag"] = [name.label for name in allName]

        return ApiResponse( result, ResposeStatus.Success )


class AddTag( Resource ):
    """
    添加元素
    tagType:Activity name,Activity type,Learnings,idea,brand,category
    name: 当选择Activity name的时候，要选择一个名字
    description:标签值
    """

    def post(self):
        data = json.loads(request.get_data(as_text=True))
        if data["tagType"] == "Activity Name":
            typeTab = Type_table()
            typeTab.name = data["description"]
            typeTab.name_type = "Activity Type"
            name = db.session.query(Name_table).filter_by( name=data["name"] ).first()
            nameId = name.id
            typeTab.name_id = nameId
            db.session.add(typeTab)
            db.session.commit()

        elif data["tagType"] == "Activity Type":
            typeTab = Type_table()
            typeTab.name = data["description"]
            typeTab.name_type = "Activity Type"
            db.session.add(typeTab)
            db.session.commit()

        else:
            tagTab = Tag()
            tagTab.label = data["description"]

            if data["tagType"] == "Learnings":
                tagTab.label_type = "Learnings"
            elif data["tagType"] == "Brand":
                tagTab.label_type = "Brand"
            elif data["tagType"] == "Idea":
                tagTab.label_type = "Idea"
            elif data["tagType"] == "Category":
                tagTab.label_type = "Category"
            db.session.add( tagTab )
            db.session.commit()

        return ApiResponse( "Already insert tag", ResposeStatus.Success )

class ShowFeedback(Resource):
    """Status: 0: all， 1: 通过， 2: 未通过， 3: 未审批"""

    def get(self):
        status = request.args.get("status")
        result = []

        if status == "0":
            data = db.session.query( Guestbook ).all()
        elif status == "1":
            data = db.session.query( Guestbook ).filter_by( state="passed" ).all()
        elif status == "2":
            data = db.session.query( Guestbook ).filter_by( state="rejected" ).all()
        elif status == "3":
            data = db.session.query( Guestbook ).filter_by( state="not reviewed" ).all()

        for i in data:
            temp = {}
            temp["id"] = i.id
            temp["type"] = i.type
            temp["description"] = i.description
            temp["time"] = i.time
            temp["state"] = i.state
            temp["userId"] = i.user_id
            result.append( temp )
        return ApiResponse( result, ResposeStatus.Success )

    def put(self):
        """
        update user feedback status
        id: The user id status will be update,
        status: 0: pass, 1: rejected
        """

        id = request.args.get("id")
        status = "passed" if request.args.get("status") == "0" else "rejected"
        session = db.session
        data = session.query(Guestbook).filter_by(id=id).first()
        data.state = status
        session.commit()

        return ApiResponse("Already update state to " + status,ResposeStatus.Success )
