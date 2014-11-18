# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Laurent OLIVIER (<lolivier@soconseil.fr>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from osv import fields, osv
import re


class classifier_trainer_wiz(osv.osv_memory):

    _name = "classifier.trainer.wiz"
    _description = "Training wizard"

    _columns = {
        'category_id': fields.many2one('classifier.category', string='Category'),
        'name': fields.text('Text for training'),
        'classifier_id' : fields.many2one('classifier','Classifier'),

        }

    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(classifier_trainer_wiz, self).default_get(cr, uid, fields, context=context)
        classifier_ids = context.get('active_ids', [])
        if not classifier_ids or (not context.get('active_model') == 'classifier') \
            or len(classifier_ids) != 1:
            return res
        classifier_id, = classifier_ids
        if 'classifier_id' in fields:
            res.update(classifier_id=classifier_id)
        return res



    def wizard_train (self, cr, uid, ids, context={}):
        record=self.browse(cr, uid, ids[0], context=context)
        if len(context['active_ids'])>1:
            return
        classif=self.pool.get('classifier').browse(cr,uid,context['active_ids'],context)[0]
        splitter=re.compile('\\W*')
      # Split the words by non-alpha characters
        items=[s.lower() for s in splitter.split(record.name)
              if len(s)>2 and len(s)<20]
        feature_train_obj=self.pool.get('classifier.train.feature')
        # Increment the count for every feature with this category
        for f in items:        
            feature_train_obj.cat_inc_f(cr,uid,classif.id,f,record.category_id.id,context)
        # Increment the count for this category
        feature_train_obj.cat_inc(cr,uid,record.category_id.id,context)
        return {'type': 'ir.actions.act_window_close'}

