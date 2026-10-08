"""Phase 0: generate the 6 starter flows (SPEC 11) as importable flow JSON using built-in pieces.

python3 -I docs/exploration/starter_flows.py <out_dir> [notify_url] [ai_provider] [ai_model]

Stand-ins (owner-approved, ADR-015): Activepieces Tables instead of Google Sheets/CRM; an HTTP POST to
`notify_url` instead of email/Slack/WhatsApp. Phase 5 turns these into real templates with placeholders.
Tables expected: externalId `opskit_leads` (name,email,message,source,received_at) and
`opskit_invoices` (customer,email,amount,due_date,status).
"""
import json
import pathlib
import sys

OUT = pathlib.Path(sys.argv[1])
NOTIFY = sys.argv[2] if len(sys.argv) > 2 else 'https://httpbin.org/post'
AI_PROVIDER = sys.argv[3] if len(sys.argv) > 3 else 'custom'
AI_MODEL = sys.argv[4] if len(sys.argv) > 4 else 'REPLACE_WITH_MODEL'
V = {'webhook': '0.1.42', 'schedule': '0.1.22', 'http': '0.12.2', 'delay': '0.3.35', 'tables': '0.5.2', 'ai': '0.11.0'}


def chain(*steps):
    for a, b in zip(steps, steps[1:]):
        a['nextAction'] = b
    return steps[0]


def piece(name, display, p, action, inp):
    return {'name': name, 'type': 'PIECE', 'valid': True, 'displayName': display, 'skip': False,
            'settings': {'pieceName': f'@activepieces/piece-{p}', 'pieceVersion': V[p], 'pieceType': 'OFFICIAL',
                         'packageType': 'REGISTRY', 'actionName': action, 'input': inp,
                         'propertySettings': {k: {'type': 'MANUAL'} for k in inp},
                         'errorHandlingOptions': {'retryOnFailure': {'value': False}, 'continueOnFailure': {'value': False}}}}


def code(name, display, src, inp):
    return {'name': name, 'type': 'CODE', 'valid': True, 'displayName': display, 'skip': False,
            'settings': {'sourceCode': {'packageJson': '{}', 'code': src}, 'input': inp, 'errorHandlingOptions': {}}}


def trigger(p, name, inp, display):
    return {'name': 'trigger', 'type': 'PIECE_TRIGGER', 'valid': True, 'displayName': display,
            'settings': {'pieceName': f'@activepieces/piece-{p}', 'pieceVersion': V[p], 'pieceType': 'OFFICIAL',
                         'packageType': 'REGISTRY', 'triggerName': name, 'input': inp,
                         'propertySettings': {k: {'type': 'MANUAL'} for k in inp}}}


def webhook_trigger():
    return trigger('webhook', 'catch_webhook', {'authType': 'none', 'authFields': {}}, 'Catch Webhook')


def notify(name, display, body):
    return piece(name, display, 'http', 'send_request', {
        'method': 'POST', 'url': NOTIFY, 'headers': {'content-type': 'application/json'}, 'queryParams': {},
        'authType': 'NONE', 'authFields': {}, 'body_type': 'json', 'body': {'data': body}, 'failsafe': False})


def reply(name, body):
    return piece(name, 'Reply to caller', 'webhook', 'return_response',
                 {'responseType': 'json', 'respond': 'stop', 'fields': {'status': 200, 'headers': {}, 'body': body}})


def router(name, display, branches, children):
    return {'name': name, 'type': 'ROUTER', 'valid': True, 'displayName': display, 'skip': False,
            'settings': {'executionType': 'EXECUTE_FIRST_MATCH', 'branches': branches}, 'children': children}


def loop(name, display, items, first):
    return {'name': name, 'type': 'LOOP_ON_ITEMS', 'valid': True, 'displayName': display, 'skip': False,
            'settings': {'items': items}, 'firstLoopAction': first}


def flow(display, trig, first):
    trig['nextAction'] = first
    return {'displayName': display, 'schemaVersion': '16', 'trigger': trig}


def lead_capture():
    t = webhook_trigger()
    return flow('01 Lead capture', t, chain(
        code('step_1', 'Validate lead', "export const code = async (i) => { if (!i.email || !String(i.email).includes('@')) throw new Error('Invalid lead: email missing'); return { name: i.name || '', email: String(i.email).toLowerCase(), message: i.message || '', source: i.source || 'website', received_at: new Date().toISOString() }; };",
             {'name': "{{trigger['body']['name']}}", 'email': "{{trigger['body']['email']}}", 'message': "{{trigger['body']['message']}}", 'source': "{{trigger['body']['source']}}"}),
        piece('step_2', 'Save lead to table', 'tables', 'tables-create-records', {'table_id': 'opskit_leads', 'values': {}, 'records': ["{{step_1}}"]}),
        notify('step_3', 'Notify owner (email stand-in)', {'type': 'new_lead', 'name': "{{step_1['name']}}", 'email': "{{step_1['email']}}", 'message': "{{step_1['message']}}"}),
        reply('step_4', {'ok': True, 'message': "Thanks {{step_1['name']}}, we'll be in touch."}),
    ))


def ai_email_sorter():
    t = webhook_trigger()
    br = [{'branchType': 'CONDITION', 'branchName': 'Urgent', 'conditions': [[{'firstValue': "{{step_1}}", 'operator': 'TEXT_EXACTLY_MATCHES', 'secondValue': 'urgent', 'caseSensitive': False}]]},
          {'branchType': 'FALLBACK', 'branchName': 'Everything else'}]
    return flow('02 AI email sorter', t, chain(
        piece('step_1', 'Classify email (AI)', 'ai', 'classifyText', {'provider': AI_PROVIDER, 'model': AI_MODEL,
              'text': "Subject: {{trigger['body']['subject']}}\n\n{{trigger['body']['body']}}", 'categories': ['urgent', 'sales', 'support', 'spam', 'other']}),
        router('step_2', 'Route by category', br, [
            notify('step_3', 'Alert team now (Slack stand-in)', {'type': 'urgent_email', 'subject': "{{trigger['body']['subject']}}", 'from': "{{trigger['body']['from']}}"}),
            code('step_4', 'Label only (Gmail label stand-in)', 'export const code = async (i) => ({ label: i.category });', {'category': "{{step_1}}"}),
        ]),
        reply('step_5', {'category': "{{step_1}}"}),
    ))


def review_request():
    t = webhook_trigger()
    return flow('03 Review request', t, chain(
        code('step_1', 'Check order', "export const code = async (i) => { if (!i.email) throw new Error('Order without customer email'); return { email: i.email, name: i.name || 'there', order: i.order_id, wait: Number(i.wait_minutes) > 0 ? Number(i.wait_minutes) : 10080 }; };",
             {'email': "{{trigger['body']['email']}}", 'name': "{{trigger['body']['name']}}", 'order_id': "{{trigger['body']['order_id']}}", 'wait_minutes': "{{trigger['body']['wait_minutes']}}"}),
        piece('step_2', 'Wait 7 days (wait_minutes overrides for tests)', 'delay', 'delayFor', {'delayFor': "{{step_1['wait']}}", 'unit': 'minutes'}),
        notify('step_3', 'Send review request (email stand-in)', {'type': 'review_request', 'to': "{{step_1['email']}}", 'text': "Hi {{step_1['name']}}, how was order {{step_1['order']}}? Leave a review: https://example.com/review"}),
    ))


def invoice_reminder():
    t = trigger('schedule', 'every_day', {'hour_of_the_day': 9, 'timezone': 'UTC', 'run_on_weekends': False}, 'Every weekday 09:00')
    return flow('04 Invoice reminder', t, chain(
        piece('step_1', 'Read invoices', 'tables', 'tables-find-records', {'table_id': 'opskit_invoices', 'filters': {}, 'limit': 1000}),
        code('step_2', 'Pick unpaid + overdue', "export const code = async (i) => { const today = new Date().toISOString().slice(0, 10); const rows = (i.rows || []).map(r => Object.fromEntries((r.cells ? Object.values(r.cells) : []).map(c => [c.fieldName, c.value]).concat(Object.entries(r).filter(([k]) => typeof r[k] !== 'object')))); const due = rows.filter(r => String(r.status || '').toLowerCase() === 'unpaid' && String(r.due_date || '9999') < today); return { due, count: due.length }; };",
             {'rows': "{{step_1}}"}),
        loop('step_3', 'For each overdue invoice', "{{step_2['due']}}",
             notify('step_4', 'Send reminder (email stand-in)', {'type': 'invoice_reminder', 'to': "{{step_3['item']['email']}}", 'customer': "{{step_3['item']['customer']}}", 'amount': "{{step_3['item']['amount']}}", 'due_date': "{{step_3['item']['due_date']}}"})),
    ))


def social_lead_alert():
    t = webhook_trigger()
    return flow('05 Social lead alert', t, chain(
        code('step_1', 'Normalise lead-ads payload', "export const code = async (i) => { const f = Object.fromEntries((i.fields || []).map(x => [x.name, x.value])); if (!f.email && !f.phone) throw new Error('Lead has no email or phone'); return { name: f.full_name || '', email: f.email || '', phone: f.phone || '', campaign: i.campaign || '' }; };",
             {'fields': "{{trigger['body']['field_data']}}", 'campaign': "{{trigger['body']['campaign_name']}}"}),
        piece('step_2', 'Add to CRM (table stand-in)', 'tables', 'tables-create-records', {'table_id': 'opskit_leads', 'values': {}, 'records': [{'name': "{{step_1['name']}}", 'email': "{{step_1['email']}}", 'message': "{{step_1['phone']}}", 'source': "ads:{{step_1['campaign']}}", 'received_at': "{{trigger['body']['created_time']}}"}]}),
        notify('step_3', 'Alert sales (WhatsApp/email stand-in)', {'type': 'social_lead', 'name': "{{step_1['name']}}", 'phone': "{{step_1['phone']}}", 'campaign': "{{step_1['campaign']}}"}),
    ))


def monthly_report():
    t = trigger('schedule', 'every_month', {'day_of_the_month': 1, 'hour_of_the_day': 8, 'timezone': 'UTC'}, 'Monthly, day 1 08:00')
    return flow('06 Monthly report', t, chain(
        piece('step_1', 'Pull numbers (sheet/API stand-in)', 'tables', 'tables-find-records', {'table_id': 'opskit_invoices', 'filters': {}, 'limit': 1000}),
        code('step_2', 'Compute KPIs', "export const code = async (i) => { const rows = (i.rows || []).map(r => Object.fromEntries((r.cells ? Object.values(r.cells) : []).map(c => [c.fieldName, c.value]))); const paid = rows.filter(r => String(r.status).toLowerCase() === 'paid'); const sum = a => a.reduce((s, r) => s + Number(r.amount || 0), 0); return { invoices: rows.length, paid: paid.length, unpaid: rows.length - paid.length, revenue: sum(paid), outstanding: sum(rows) - sum(paid) }; };",
             {'rows': "{{step_1}}"}),
        piece('step_3', 'Write summary (AI)', 'ai', 'summarizeText', {'provider': AI_PROVIDER, 'model': AI_MODEL, 'text': "{{step_2}}",
              'prompt': 'Write a short, friendly monthly business summary (max 120 words) for the client from these KPIs. Mention revenue, outstanding amount and one suggestion.'}),
        notify('step_4', 'Email report (email stand-in)', {'type': 'monthly_report', 'kpis': "{{step_2}}", 'summary': "{{step_3}}"}),
    ))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for fn in (lead_capture, ai_email_sorter, review_request, invoice_reminder, social_lead_alert, monthly_report):
        f = fn()
        path = OUT / (f['displayName'].split(' ', 1)[0] + '-' + fn.__name__.replace('_', '-') + '.json')
        path.write_text(json.dumps(f, indent=1))
        print(path)


if __name__ == '__main__':
    main()
