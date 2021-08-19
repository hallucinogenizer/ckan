import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


def newest_datasets():
    datasets = toolkit.get_action('package_search')(data_dict={'sort':'metadata_modified desc','rows':4})
    return datasets

def popular_datasets():
    datasets = toolkit.get_action('package_search')(data_dict={'sort':'views_recent desc','rows':4})
    return datasets

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


class DatasetCategoriesPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IFacets)

    def update_config(self, config):
        pass

    def dataset_facets(self, facets_dict, package_type):
        facets_dict['categories'] = toolkit._('Categories')
        return facets_dict

class DatasetFacetPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(p.IDatasetForm)

    def create_package_schema(self):
        # let's grab the default schema in our plugin
        schema = super(DatasetFacetPlugin, self).create_package_schema()
        # our custom field
        schema.update({
            'Category': [toolkit.get_validator('ignore_missing'),
                        toolkit.get_converter('convert_to_extras')]
        })
        return schema

    def update_package_schema(self):
        # let's grab the default schema in our plugin
        schema = super(DatasetFacetPlugin, self).create_package_schema()
        # our custom field
        schema.update({
            'Category': [toolkit.get_validator('ignore_missing'),
                        toolkit.get_converter('convert_to_extras')]
        })
        return schema

    def show_package_schema(self):
        schema = super(DatasetFacetPlugin, self).show_package_schema()
        schema.update({
            'custom_text': [tk.get_converter('convert_from_extras'),
                            tk.get_validator('ignore_missing')]
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