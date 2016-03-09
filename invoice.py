# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from decimal import Decimal

from trytond.pool import PoolMeta, Pool
from trytond.model import ModelView, Workflow, fields
from trytond.pyson import Eval, If, Bool
from trytond.transaction import Transaction
from trytond.tools import grouped_slice

__all__ = ['Invoice', 'InvoiceLine']
__metaclass__ = PoolMeta


class Invoice:
    __name__ = 'account.invoice'
    agent = fields.Many2One('commission.agent', 'Commission Agent',
        domain=[
            ('company', '=', Eval('company', -1)),
            ],
        states={
            'invisible': Eval('type').in_(['in_invoice', 'in_credit_note']),
            'readonly': Eval('state', '') != 'draft',
            },
        depends=['type', 'company', 'state'])

    @classmethod
    @ModelView.button
    @Workflow.transition('posted')
    def post(cls, invoices):
        super(Invoice, cls).post(invoices)
        cls.create_commissions(invoices)

    @classmethod
    def create_commissions(cls, invoices):
        pool = Pool()
        Commission = pool.get('commission')
        all_commissions = []
        for invoice in invoices:
            for line in invoice.lines:
                commissions = line.get_commissions()
                if commissions:
                    all_commissions.extend(commissions)

        with Transaction().set_context(_check_access=False):
            return Commission.create([c._save_values for c in all_commissions])

    @classmethod
    @Workflow.transition('paid')
    def paid(cls, invoices):
        pool = Pool()
        Date = pool.get('ir.date')
        Commission = pool.get('commission')

        today = Date.today()

        super(Invoice, cls).paid(invoices)

        for sub_invoices in grouped_slice(invoices):
            ids = [i.id for i in sub_invoices]
            commissions = Commission.search([
                    ('date', '=', None),
                    ('origin.invoice', 'in', ids, 'account.invoice.line'),
                    ])
            with Transaction().set_context(_check_access=False):
                Commission.write(commissions, {
                        'date': today,
                        })

    @classmethod
    @ModelView.button
    @Workflow.transition('cancel')
    def cancel(cls, invoices):
        pool = Pool()
        Commission = pool.get('commission')

        super(Invoice, cls).cancel(invoices)

        to_delete = []
        to_write = []
        for sub_invoices in grouped_slice(invoices):
            ids = [i.id for i in sub_invoices]
            to_delete += Commission.search([
                    ('invoice_line', '=', None),
                    ('origin.invoice', 'in', ids, 'account.invoice.line'),
                    ])
            to_cancel = Commission.search([
                    ('invoice_line', '!=', None),
                    ('origin.invoice', 'in', ids, 'account.invoice.line'),
                    ])
            for commission in Commission.copy(to_cancel):
                commission.amount * -1
                to_write.extend(([commission], {
                            'amount': commission.amount * -1,
                            }))

        Commission.delete(to_delete)
        if to_write:
            Commission.write(*to_write)

    def _credit(self):
        values = super(Invoice, self)._credit()
        values['agent'] = self.agent.id if self.agent else None
        return values


class InvoiceLine:
    __name__ = 'account.invoice.line'
    principal = fields.Many2One('commission.agent', 'Commission Principal',
        domain=[
            ('type_', '=', 'principal'),
            ('company', '=', Eval('_parent_invoice', {}).get('company',
                    Eval('company', -1))),
            ],
        states={
            'invisible': If(Bool(Eval('_parent_invoice')),
                Eval('_parent_invoice', {}).get('type').in_(
                    ['in_invoice', 'in_credit_note']),
                Eval('invoice_type').in_(
                    ['in_invoice', 'in_credit_note'])),
            }, depends=['invoice_type', 'company'])
    commissions = fields.One2Many('commission', 'origin', 'Commissions',
        readonly=True,
        states={
            'invisible': ~Eval('commissions'),
            })
    from_commissions = fields.One2Many('commission', 'invoice_line',
        'From Commissions', readonly=True,
        states={
            'invisible': ~Eval('from_commissions'),
            })

    @property
    def agent_plans_used(self):
        "List of agent, plan tuple"
        used = []
        if self.invoice.agent:
            used.append((self.invoice.agent, self.invoice.agent.plan))
        if self.principal:
            used.append((self.principal, self.principal.plan))
        return used

    def get_commissions(self):
        pool = Pool()
        Commission = pool.get('commission')
        Currency = pool.get('currency.currency')
        Date = pool.get('ir.date')

        if self.type != 'line':
            return []

        today = Date.today()
        commissions = []
        for agent, plan in self.agent_plans_used:
            if not plan:
                continue
            with Transaction().set_context(date=self.invoice.currency_date):
                amount = Currency.compute(self.invoice.currency,
                    self.amount, agent.currency, round=False)
            if self.invoice.type == 'out_credit_note':
                amount *= -1
            amount = self._get_commission_amount(amount, plan)
            if amount:
                digits = Commission.amount.digits
                amount = amount.quantize(Decimal(str(10.0 ** -digits[1])))
            if not amount:
                continue

            commission = Commission()
            commission.origin = self
            if plan.commission_method == 'posting':
                commission.date = today
            commission.agent = agent
            commission.product = plan.commission_product
            commission.amount = amount
            commissions.append(commission)
        return commissions

    def _get_commission_amount(self, amount, plan, pattern=None):
        return plan.compute(amount, self.product, pattern=pattern)

    @fields.depends('product', 'principal')
    def on_change_product(self):
        changes = super(InvoiceLine, self).on_change_product()
        if self.product:
            if self.product.principals:
                if self.principal not in self.product.principals:
                    changes['principal'] = self.product.default_principal.id
            elif self.principal:
                changes['principal'] = None
        return changes

    @classmethod
    def copy(cls, lines, default=None):
        if default is None:
            default = {}
        default.setdefault('commissions', None)
        default.setdefault('from_commissions', None)
        return super(InvoiceLine, cls).copy(lines, default)
