import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from collections import OrderedDict

preset_categories = ['Public Safety','Economy & Finance','Government & Public Sector','Demography','Health','Environment & Energy','Education','Cities & Regions','Housing & Public Services','Connectivity','Agriculture, Food, & Forests','Manufacturing','Science & Technology','Culture']

def newest_datasets():
    datasets = toolkit.get_action('package_search')(data_dict={'sort':'metadata_modified desc','rows':4})
    return datasets

def popular_datasets():
    datasets = toolkit.get_action('package_search')(data_dict={'sort':'views_recent desc','rows':4})
    return datasets

def list_to_comma_separated_string(list):
    return ", ".join(list)

def num_datasets_in_organization(org_id):
    num_datasets = toolkit.get_action('organization_show')(data_dict=
    {
        'id':org_id,
        'include_dataset_count':True,
        'include_datasets':True
    })
    return num_datasets

def get_package_views(package_id):
    package_views = toolkit.get_action('package_show')(data_dict={'id':package_id,'include_tracking':True})
    return package_views

def get_packages_in_category(category,package_id):
    # get all similar packages, except the same package (the one that has id=package_id)
    datasets = toolkit.get_action('package_search')(data_dict={'sort':'views_recent desc'})
    final_datasets = []
    x=0
    for dataset in datasets["results"]:
        if (dataset["category"]==category and dataset["id"]!=package_id):
            if (x!=3):
                final_datasets.append(dataset)
                x=x+1
            else:
                break
    return final_datasets

def default_category_validator(value):
    if value in preset_categories:
        return value
    else:
        raise toolkit.Invalid("Please select a value other than the default one.")

def get_preset_categories():
    list = []
    list.append({'text':'Select a value', 'value': 'None'})
    for category in preset_categories:
        list.append({'text':category, 'value':category})
    return list

def create_locations():
    user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
    context = {'user': user['name']}
    try:
        data = {'id': 'locations'}
        toolkit.get_action('vocabulary_show')(context, data)
    except toolkit.ObjectNotFound:
        data = {'name': 'locations'}
        vocab = toolkit.get_action('vocabulary_create')(context, data)
        for tag in (u'Lahore', u'Islamabad', u'Karachi', u'Multan', u'Peshawar'):
            data = {'name': tag, 'vocabulary_id': vocab['id']}
            toolkit.get_action('tag_create')(context, data)

def locations():
    create_locations()
    try:
        tag_list = toolkit.get_action('tag_list')
        current_locations = tag_list(data_dict={'vocabulary_id': 'locations'})
        return current_locations
    except toolkit.ObjectNotFound:
        return None

class ExampleThemePlugin(plugins.SingletonPlugin):
    '''An example theme plugin.

    '''
    # Declare that this class implements IConfigurer.
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    def update_config(self, config):

        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        # 'templates' is the path to the templates dir, relative to this
        # plugin.py file.
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_public_directory(config, 'public')
        toolkit.add_resource('fantastic', 'example_theme')

    def get_helpers(self):
        return {'example_theme_newest_datasets':newest_datasets, 'example_theme_popular_datasets':popular_datasets,
        'num_datasets_in_organization':num_datasets_in_organization,
        'get_package_views':get_package_views,
        'list_to_comma_separated_string':list_to_comma_separated_string,
        'get_packages_in_category':get_packages_in_category}

class ExampleIDatasetFormPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IDatasetForm)
    # plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IValidators)
    plugins.implements(plugins.ITemplateHelpers)


    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'datasetlocations')

    # IDatasetForm
    def get_helpers(self):
        return {'locations': locations,'get_preset_categories':get_preset_categories}

    # My custom converter
    plugins.implements(plugins.IValidators)
    def get_validators(self):
        return {'default_category_validator':default_category_validator}

    def _modify_package_schema(self, schema):
        schema.update({
            'category': [toolkit.get_validator('default_category_validator'),
            toolkit.get_converter('convert_to_extras')]
        })
        schema.update({
            'locations': [
                            toolkit.get_converter('convert_to_tags')('locations'),
                            toolkit.get_validator('ignore_missing')]
        })

        return schema

    def create_package_schema(self):
        # let's grab the default schema in our plugin
        schema = super(ExampleIDatasetFormPlugin, self).create_package_schema()
        # our custom field
        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super(ExampleIDatasetFormPlugin, self).update_package_schema()
        # our custom field
        schema = self._modify_package_schema(schema)
        return schema

    def show_package_schema(self):
        schema = super(ExampleIDatasetFormPlugin, self).show_package_schema()
        schema.update({
            'category': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('default_category_validator')]
        })
        schema['tags']['__extras'].append(toolkit.get_converter('free_tags_only'))
        schema.update({
            'locations': [
                toolkit.get_converter('convert_from_tags')('locations'),
                toolkit.get_validator('ignore_missing')]
            })
        return schema

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []
