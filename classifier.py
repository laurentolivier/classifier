#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  soc_nota.py
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
from openerp.tools.translate import _
import re


class classifier(osv.osv):

    _name = "classifier"
    _description = "Analysis object used to class objects"
    _columns = {
        'name':fields.char('name', size=64),
        'description':fields.text('Description'),
        #'category_ids': fields.many2many('classifier.category', id1='category_id', id2='classifier_id', string='Tags'),
        'category_ids': fields.one2many('classifier.category', 'classifier_id', string='Categories'),
        'train_features_ids' : fields.one2many('classifier.train.feature','classifier_id','Feature Trainings'),
      }

    def getwords(self,cr,uid,doc):
      splitter=re.compile('\\W*')
      # Split the words by non-alpha characters
      words=[s.lower() for s in splitter.split(doc)
              if len(s)>2 and len(s)<20]
      # Return the unique set of words only
      return dict([(w,1) for w in words])


    def fcount(self,cr,uid,classifier,f,category):
        '''count how many time a feature has been trained for this category '''
        train_obj=self.pool.get('classifier.train.feature')
        train_ids=train_obj.search(cr,uid,[('category_id','=',category.id),('classifier_id','=',classifier.id),('feature','=',f)])
        if train_ids:
            train=train_obj.browse(cr,uid,train_ids)[0] #there is only one
            return train.counter
        else:
            return 0

    def totalcount(self,cr,uid,classifier):
        '''count how many time all category has been trained '''
        total=0
        for category in classifier.category_ids:
            total+=category.counter
        return total


    def fprob(self,cr,uid,classifier,f,category):
        catcount=category.counter
        fcount=self.fcount(cr,uid,classifier, f, category)
        if catcount==0:
            res=0
        else:
            res=float(fcount)/catcount
        return res

    def weightedprob(self,cr,uid,classifier,f,category,prf,weight=1.0,ap=0.5):
        basicprob=prf(cr,uid,classifier,f,category)
        totals=0
        # Count the number of times this feature has appeared in
        # all categories
        train_obj=self.pool.get('classifier.train.feature')
        train_ids=train_obj.search(cr,uid,[('classifier_id','=',classifier.id),('feature','=',f)])
        if train_ids:
            for train in train_obj.browse(cr,uid,train_ids):
                totals+=train.counter
        # Calculate the weighted average
        res=((weight*ap)+(totals*basicprob))/(weight+totals)
        return res

    def docprob(self,cr,uid,classifier,item,category):
        features=self.getwords(cr,uid,item)
        # Multiply the probabilities of all the features together
        p=1
        for f in features:
            p2=self.weightedprob(cr,uid,classifier,f,category,self.fprob)
            p*=p2
        return p

    def prob(self,cr,uid,classifier,item,category):
        catcount=category.counter
        totalcount=self.totalcount(cr,uid,classifier)
        catprob=float(catcount)/totalcount
        docprob=self.docprob(cr,uid,classifier,item,category)
        return docprob*catprob

class classifier_train_feature(osv.osv):
    _name = "classifier.train.feature"
    _description = "Record of feature training . Used for analysis other objects"
    _columns = {
        'category_id': fields.many2one('classifier.category', string='Category'),
        'feature': fields.char('Feature',size=128),
        'counter':fields.integer('Count'),
        'classifier_id' : fields.many2one('classifier','Classifier'),
      }

    def cat_inc_f (self,cr,uid,classifier_id,f,category_id,context=None):
        """ Increment the count for every feature with this category """
        train_id=self.search(cr,uid,[('feature','=',f),('classifier_id','=',classifier_id),('category_id','=',category_id)])
        if not(train_id):
          vals={
            'feature': f,
            'counter': 1,
            'category_id' : category_id,
            'classifier_id' : classifier_id,
              }
          self.create(cr,uid,vals,context)
        else:
          count_old=self.browse(cr,uid,train_id,context)[0].counter
          self.write(cr,uid,train_id,{'counter':count_old+1})

        return True

    def cat_inc (self,cr,uid,category_id,context=None):
        """ Increment the counter for this category """
        count_old=self.pool.get('classifier.category').browse(cr,uid,category_id).counter or 0
        self.pool.get('classifier.category').write(cr,uid,category_id,{'counter':count_old+1})
        return True



class classifier_category(osv.osv):
    _description = 'Classifier Categories'
    _name = 'classifier.category'


    def name_get(self, cr, uid, ids, context=None):
        """Return the categories' display name, including their direct
           parent by default.

        :param dict context: the ``classifier_category_display`` key can be
                             used to select the short version of the
                             category name (without the direct parent),
                             when set to ``'short'``. The default is
                             the long version."""
        if context is None:
            context = {}
        if context.get('classifier_category_display') == 'short':
            return super(classifier_category, self).name_get(cr, uid, ids, context=context)
        if isinstance(ids, (int, long)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name', 'parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1] + ' / ' + name
            res.append((record['id'], name))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if not context:
            context = {}
        if name:
            # Be sure name_search is symetric to name_get
            name = name.split(' / ')[-1]
            ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)


    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)


    _columns = {
        'name': fields.char('Category Name', required=True, size=64, translate=True),
        'parent_id': fields.many2one('classifier.category', 'Parent Category', select=True, ondelete='cascade'),
        'complete_name': fields.function(_name_get_fnc, type="char", string='Full Name'),
        'child_ids': fields.one2many('classifier.category', 'parent_id', 'Child Categories'),
        'active': fields.boolean('Active', help="The active field allows you to hide the category without removing it."),
        'parent_left': fields.integer('Left parent', select=True),
        'parent_right': fields.integer('Right parent', select=True),
        'document_ids': fields.many2many('ir.attachment', id1='category_id', id2='document_id', string='Documents'),
        'counter': fields.integer('Training counter', readonly=True),
        'classifier_id': fields.many2one('classifier', string='Classifier'),
    }
    _constraints = [
        (osv.osv._check_recursion, 'Error ! You can not create recursive categories.', ['parent_id'])
    ]
    _defaults = {
        'active': 1,
    }
    _parent_store = True
    _parent_order = 'name'
    _order = 'parent_left'

