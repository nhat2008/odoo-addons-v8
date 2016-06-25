
// This file contains the Screens definitions. Screens are the
// content of the right pane of the pos, containing the main functionalities. 
//
// Screens must be defined and named in chrome.js before use.
//
// Screens transitions are controlled by the Gui.
//  gui.set_startup_screen() sets the screen displayed at startup
//  gui.set_default_screen() sets the screen displayed for new orders
//  gui.show_screen() shows a screen
//  gui.back() goes to the previous screen
//
// Screen state is saved in the order. When a new order is selected,
// a screen is displayed based on the state previously saved in the order.
// this is also done in the Gui with:
//  gui.show_saved_screen()
//
// All screens inherit from ScreenWidget. The only addition from the base widgets
// are show() and hide() which shows and hides the screen but are also used to 
// bind and unbind actions on widgets and devices. The gui guarantees
// that only one screen is shown at the same time and that show() is called after all
// hide()s
//
// Each Screens must be independant from each other, and should have no 
// persistent state outside the models. Screen state variables are reset at
// each screen display. A screen can be called with parameters, which are
// to be used for the duration of the screen only. 
openerp.pos_access_modification = function(instance){
    var module = instance.point_of_sale; // loading the namespace of the 'sample' module

    var PosModelSuper = module.PosModel;

    module.PosModel = module.PosModel.extend({
        
        initialize: function(session, attributes) {
            var self = this;
            var loaded = PosModelSuper.prototype.initialize.call(this,session, attributes);
            this.manager_group = null;
            this.login_employee_groups = [];
            this.get_manager_group();
            this.get_login_employee_groups();
        },

        get_manager_group: function(){
            var self = this;
            var res_groups = new openerp.web.Model('res.groups');
            console.log(self.user);
            res_groups.call('search', [[['full_name', '=', 'Point of Sale / Manager']]]).then(function(value){
                // this call function will be run after the function initialize. You can use console.log to see how it works
                self.manager_group = value[0];
            });
        },
        get_login_employee_groups: function(){
            var self = this;
            var res_groups = new openerp.web.Model('res.users');
            res_groups.call('search_read', [[['id', '=', self.session.uid]],['groups_id']]).then(function(value){
                // this call function will be run after the function initialize. You can use console.log to see how it works
                self.login_employee_groups = value[0];
            });
            
        },

    });
            
    module.OrderWidget.include({
        set_value : function(val){
            var order = this.pos.get_order();
            if (order.getSelectedLine()) {
                var mode = this.numpad_state.get('mode');
                // Issue 009    
                // GET Logged User

                // alert(this.pos.login_employee_groups.groups_id);
                // console.log(this.pos.login_employee_groups.groups_id);
                // console.log(this.pos.manager_group);
                var user = this.pos.login_employee_groups;

                // GET ID of Local Admin
                var manager_id = this.pos.manager_group;
                if( mode === 'quantity'){
                    order.getSelectedLine().set_quantity(val);
                }else if( mode === 'discount'){
                    for (var j = 0; j< user.groups_id.length; j++)
                    {
                        // alert(user.groups_id[j]);
                        if (user.groups_id[j] == manager_id)
                        {
                            order.getSelectedLine().set_discount(val);
                            break;
                        }
                    }
                    
                }else if( mode === 'price'){
                    // FIND If logged user have POS manager in groups
                    for (var j = 0; j< user.groups_id.length; j++)
                    {
                        // alert(user.groups_id[j]);
                        if (user.groups_id[j] == manager_id)
                        {
                            order.getSelectedLine().set_unit_price(val);
                            break;
                        }
                    }
                }
            }
        },
    });

//  Thu.vo Modified 26-05-2015
//  Start   
    module.NumpadWidget.include({
         init: function(parent, options) {
            // alert("Init");
            //console.log("init");
            this._super(parent, options);
            // inherit from NumpadWidget, then define a new field
            // This field defines what mode is selected
            this.selected_mode = 'quantity';
        },

        clickSwitchSign: function() {               // Override clickSwitchSign function of Numpadwdget
            //console.log("Switch");
            if(this.selected_mode === 'quantity')   // if the selected mode is 'quantity'
                return;                             // do not accept negative quantity
            return this.state.switchSign();      
        },
        
        clickAppendNewChar: function(event) {       // Override clickAppendNewChar function
            var newChar;
            //console.log("New char");
            newChar = event.currentTarget.innerText || event.currentTarget.textContent;     // get the pressed key
                if(newChar === '.' && this.selected_mode === 'quantity')                    // if the key is '.' and in quantity mode
                    return;                                                                 // do not accept
            return this.state.appendNewChar(newChar);
        },
        
        clickChangeMode: function(event) {
            var newMode = event.currentTarget.attributes['data-mode'].nodeValue;
            this.selected_mode = newMode;
            //console.log("New mode");
            return this.state.changeMode(newMode);
        },
    });
// End

//  Thu.vo Modified 01-06-2015
// Disable print popup when validating order
//  Start  
    module.ReceiptScreenWidget.include({
        show: function(){
            this.pos.get('selectedOrder')._printed = true;
            this._super();
        },
    });
// End
};