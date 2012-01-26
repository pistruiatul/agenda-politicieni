import sys, re
import simplejson as json

p = re.compile(r'^(?P<last>[\w\-]+)\s+(?P<initial>\w+\.\s+)?(?P<first>[\w\s\-]+)$',
               re.UNICODE)

S = json.load(sys.stdin)

for s in S:
  s['inverse_name'] = s['name']
  m = p.match(s['inverse_name'])
  s['name'] = u'%s %s' % m.group('first', 'last')

json.dump(S, sys.stdout, indent=2)
