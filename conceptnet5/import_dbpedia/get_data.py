"""
Get data from DBPedia.
"""

__author__ = 'Justin Venezuela (jven@mit.edu)'

from conceptnet5.graph import JSONWriterGraph
import urllib2

DBPEDIA_DATA_PREFIX = u'http://dbpedia.org/page/'
DBPEDIA_SOURCE = [u'source', u'web', u'dbpedia.org']
TYPE_HTML = ('<a class="uri" href="http://www.w3.org/1999/02/'
    '22-rdf-syntax-ns#type">')
TYPE_RELATION_NAME = u'InstanceOf'
TYPE_RELATION_PROPERTIES = {
    'owl:sameAs':u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
}
TYPE_ASSERTION_PROPERTIES = {
    'source':u'dbpedia',
    'license':u'CC-By-SA'
}
WIKIPEDIA_TITLES = 'breadth-first-articles.txt'

VERBOSE = True

def set_node_properties(node, properties):
  for key in properties:
    node[key] = properties[key]

def show_message(message):
  if VERBOSE:
    print message

def get_url_from_obj_name(obj_name):
  obj_url = DBPEDIA_DATA_PREFIX + obj_name
  return obj_url

def get_html_from_url(url):
  page = urllib2.urlopen(url)
  html = page.read()
  page.close()
  return html

def get_types_from_html(html):
  if TYPE_HTML not in html:
    return []
  obj_types = []
  html = html.split(TYPE_HTML, 1)[1].split('<ul>', 1)[1].split('</ul>', 1)[0]
  while 'href="' in html:
    [obj_type, html] = html.split('href="', 1)[1].split('">', 1)
    obj_types.append(obj_type)
  print obj_types
  return obj_types

def make_type_assertions_for_obj(conceptnet, obj_url, obj_types):
  concept = conceptnet.get_or_create_web_concept(obj_url)
  for obj_type in obj_types:
    obj_type_concept = conceptnet.get_or_create_web_concept(obj_type)
    assertion = conceptnet.get_or_create_assertion(
        '/relation/'+TYPE_RELATION_NAME, [concept, obj_type_concept],
        properties=TYPE_ASSERTION_PROPERTIES)
    #set_node_properties(assertion, TYPE_ASSERTION_PROPERTIES)
    conceptnet.justify(source, assertion)

def main():
  wikipediaTitles = open(WIKIPEDIA_TITLES)
  conceptnet = JSONWriterGraph('json_data/dbpedia_data')
  source = conceptnet.get_or_create_source(DBPEDIA_SOURCE)
  conceptnet.justify('/', source)
  instanceOf = conceptnet.get_or_create_relation(TYPE_RELATION_NAME,
    properties=TYPE_RELATION_PROPERTIES)
  for line in wikipediaTitles:
    try:
      obj_name = line.strip().decode('utf-8')
    except Exception:
      show_message(u'WARNING: Could not decode \'%s\'.' % line)
      continue
    # get data from dbpedia
    obj_url = get_url_from_obj_name(obj_name)
    try:
      html = get_html_from_url(obj_url)
    except Exception:
      show_message(
          u'WARNING: Could not get DBPedia page for \'%s\'.' % obj_name)
      continue
    obj_types = get_types_from_html(html)
    # interact with graph
    make_type_assertions_for_obj(conceptnet, obj_url, obj_types)
  show_message(u'NOTICE: Script finished!')

if __name__ == '__main__':
  main()
