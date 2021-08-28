import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

preset_categories = ['Public Safety','Economy & Finance','Government & Public Sector','Demography','Health','Environment & Energy','Education','Cities & Regions','Housing & Public Services','Connectivity','Agriculture, Food, & Forests','Manufacturing','Science & Technology','Culture']

def newest_datasets():
    datasets = toolkit.get_action('package_search')(data_dict={'sort':'metadata_modified desc','rows':4})
    return datasets

def popular_datasets():
    datasets = toolkit.get_action('package_search')(data_dict={'sort':'views_recent desc','rows':4})
    return datasets

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
        return {'example_theme_newest_datasets':newest_datasets, 'example_theme_popular_datasets':popular_datasets}



class ExampleIDatasetFormPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IDatasetForm)
    # plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IValidators)
    plugins.implements(plugins.ITemplateHelpers)


    def get_validators(self):
        return {'default_category_validator':default_category_validator}

    def get_helpers(self):
        return {'get_preset_categories':get_preset_categories}

    def _modify_package_schema(self, schema):
        schema.update({
            'category': [toolkit.get_validator('default_category_validator'),
            toolkit.get_converter('convert_to_extras')]
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
        return schema

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []
