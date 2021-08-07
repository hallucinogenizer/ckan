import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


def newest_datasets():
    datasets = toolkit.get_action('package_search')(data_dict={'sort':'metadata_modified desc','rows':4})
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
        return {'example_theme_newest_datasets':newest_datasets}