ckan.module('cloudstorage-storage', function($, _){
    "use strict";
    return {
        initialize: function(){
            $.proxyAll(this, /_on/);
            var store_on = jQuery('#setting-store-on');
            var settings_group = jQuery('fieldset.settings-groups');
            this._onLoad(store_on, settings_group);
            this.el.on('change', this._onChange);
        },
        _onLoad: function(store_on, settings_group){
            var selected_option = this.el['0']['selectedOptions']['0'].value;
            if (selected_option != 'Filestorage'){
                var selected_store = jQuery('#field-store_on')['0']['selectedOptions']['0'].value;
                store_on.show();
                store_on.removeAttr('disabled');
                jQuery('#settings-' + selected_store).removeAttr('disabled');
                jQuery('#settings-' + selected_store).show();
            }
            else{
                store_on.hide();
                store_on.attr('disabled', '');
                settings_group.attr('disabled', '');
                settings_group.hide();
            };
        },
        _onChange: function(e){
            var selected_option = this.el['0']['selectedOptions']['0'].value;
            if (selected_option != 'Filestorage'){
                console.log(jQuery('#field-store_on')['0']['selectedOptions']['0'].value);
                var selected_store = jQuery('#field-store_on')['0']['selectedOptions']['0'].value;
                jQuery('#setting-store-on').show();
                jQuery('#setting-store-on').removeAttr('disabled');
                jQuery('#settings-' + selected_store).removeAttr('disabled');
                jQuery('#settings-' + selected_store).show();
            }
            else{
                jQuery('#setting-store-on').hide();
                jQuery('#setting-store-on').attr('disabled', '');
                jQuery('fieldset.settings-groups').attr('disabled', '');
                jQuery('fieldset.settings-groups').hide();
            };
        },
    };
});
