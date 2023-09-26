from flask import request
from flask_restx import Resource
from sqlalchemy import and_

from src import api
from src.lib.WHE_scrape import whe_scrape
from src.models.decisions import Decision

@api.route('/search')
class Search(Resource):
    def get(self):
        keyword = request.args.get('keyword')
        examiner = request.args.get('examiner')
        hearing_date = request.args.get('hearingDate')
        decision_date = request.args.get('decisionDate')

        filters = []
        if keyword:
          filters.append(Decision.text.ilike(f'%{keyword}%'))
        if examiner:
          filters.append(Decision.hearing_examiner.ilike(f'%{examiner}%'))
        if hearing_date:
          filters.append(Decision.hearing_date.ilike(f'%{hearing_date}%'))
        if decision_date:
          filters.append(Decision.decision_date.ilike(f'%{decision_date}%'))
        
        search_results = Decision.query.filter(and_(*filters))
        print(search_results)

        result_list = [{
            'id': decision.id,
            'case_name': decision.case_name,
            'hearing_examiner': decision.hearing_examiner,
            'hearing_date': decision.hearing_date,
            'decision_date': decision.decision_date,
            'text': decision.text,
            'link': decision.link
        } for decision in search_results]

        return {'search_results': result_list}

@api.route('/metadata')
class Metadata(Resource):
  def get(self):
    return {'metadata': whe_scrape.get_metadata()}

