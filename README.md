XING PARSER:

Used technologies: Django, Scrapy
Used DB: PostgreSQL


DEPLOYMENT:
	scrapyd

	SET absolute path. Example:
		DJANGO_PROJECT_PATH = '/home/ubuntu/xing_parser/xing_django'
		DJANGO_SETTINGS_MODULE = 'xing_django.settings'
		in scrapy project settings_local.py

	scrapyd-deploy scrapyd -p search_employees