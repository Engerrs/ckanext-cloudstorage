ckan.module('cloudstorage-store-on', function($, _){
    "use strict";
    return {
        initialize: function(){
            $.proxyAll(this, /_on/);
            this._onLoad();
            this.el.on('change', this._onChange);
        },
        _onLoad: function(){
            var selected_option = this.el['0']['selectedOptions']['0'].value;
            if (selected_option != 'Select Store'){
                jQuery('#settings-' + selected_option).removeAttr('disabled');
                jQuery('#settings-' + selected_option).show();
            }
            else{
                jQuery('fieldset.settings-groups').attr('disabled', '');
                jQuery('fieldset.settings-groups').hide();
            };
        },
        _onChange: function(e){
            var selected_option = this.el['0']['selectedOptions']['0'].value;
            if (selected_option != 'Select Store'){
                jQuery('#settings-' + selected_option).removeAttr('disabled');
                jQuery('#settings-' + selected_option).show();
            }
            else{
                jQuery('fieldset.settings-groups').attr('disabled', '');
                jQuery('fieldset.settings-groups').hide();
            };
        },
    };
});
