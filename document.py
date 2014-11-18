#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  document.py
#
#  Copyright 2014 Laurent OLIVIER <lolivier@soconseil.fr>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

from openerp.osv import fields, osv


class document_file (osv.osv):
    _inherit = 'ir.attachment'

    _columns = {
        'category_ids': fields.many2many('classifier.category', id1='document_id', id2='category_id', string='Categories'),
        }

    def classifiy(self,cr,uid,ids,classifiers,default=None,context=None):

        if context==None:
            context={}
        classifier_obj=self.pool.get('classifier')
        for doc in self.browse(cr,uid,ids,context):
            if doc.index_content==None:
                return default
            item=doc.index_content
            for classifier in classifiers:
                best={}
                probs={}
                max1=0.0
                for cat in classifier.category_ids:
                  probs[cat.id]=classifier_obj.prob(cr,uid,classifier,item,cat)                  
                  if probs[cat.id]>max1:
                    max1=probs[cat.id]
                    best[classifier.id]=cat
            new_ids=[]
            old_ids=[x.id for x in doc.category_ids] or []
            for v in best.values():
                if  v.id not in old_ids : new_ids.append(v.id)
            old_ids.extend(new_ids)
            final_ids=[(6, 0)+(old_ids,)]
            self.write(cr,uid,doc.id,{'category_ids':final_ids})

        return
