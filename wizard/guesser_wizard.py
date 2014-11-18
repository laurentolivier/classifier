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
from tools.translate import _



class classifier_guesser_wiz(osv.osv_memory):

    _name = "classifier.guesser.wiz"
    _description = "Guessing wizard"

    _columns = {        
      #  'classifier_id' : fields.many2one('classifier','Classifier'),
        'classifier_ids' : fields.many2many('classifier','guesser_classifier_rel','guesser_id','classifier_id','Classifier'),
        }


    def wizard_guess (self, cr, uid, ids, context={}):
        record=self.browse(cr, uid, ids[0],context)
        doc_obj=self.pool.get('ir.attachment')
        doc_obj.classifiy(cr,uid,context['active_ids'],record.classifier_ids,context=context)
        return {'type': 'ir.actions.act_window_close'}

