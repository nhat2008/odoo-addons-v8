
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
openerp.pos_order_contraints = function(instance){
    var module = instance.point_of_sale; // loading the namespace of the 'sample' module
    _t = instance.web._t;
    
    module.PaymentScreenWidget.include({
        
        after_validate_order: function(options,currentOrder) {
            var self = this;
            // Orinal
            if(currentOrder.get('orderLines').models.length === 0){
                    self.pos_widget.screen_selector.show_popup('error',{
                        'message': _t('Empty Order'),
                        'comment': _t('There must be at least one product in your order before it can be validated'),
                    });
                    return;
            }

            var plines = currentOrder.get('paymentLines').models;
            for (var i = 0; i < plines.length; i++) {
                if (plines[i].get_type() === 'bank' && plines[i].get_amount() < 0) {
                    self.pos_widget.screen_selector.show_popup('error',{
                        'message': _t('Negative Bank Payment'),
                        'comment': _t('You cannot have a negative amount in a Bank payment. Use a cash payment method to return money to the customer.'),
                    });
                    return;
                }
            }

            if(!self.is_paid()){
                return;
            }
            
            // The exact amount must be paid if there is no cash payment method defined.
            if (Math.abs(currentOrder.getTotalTaxIncluded() - currentOrder.getPaidTotal()) > 0.00001) {
                var cash = false;
                for (var i = 0; i < self.pos.cashregisters.length; i++) {
                    cash = cash || (self.pos.cashregisters[i].journal.type === 'cash');
                }
                if (!cash) {
                    self.pos_widget.screen_selector.show_popup('error',{
                        message: _t('Cannot return change without a cash payment method'),
                        comment: _t('There is no cash payment method available in this point of sale to handle the change.\n\n Please pay the exact amount or add a cash payment method in the point of sale configuration'),
                    });
                    return;
                }
            }

            if (self.pos.config.iface_cashdrawer) {
                    self.pos.proxy.open_cashbox();
            }

            if(options.invoice){
                // deactivate the validation button while we try to send the order
                self.pos_widget.action_bar.set_button_disabled('validation',true);
                self.pos_widget.action_bar.set_button_disabled('invoice',true);

                var invoiced = self.pos.push_and_invoice_order(currentOrder);

                invoiced.fail(function(error){
                    if(error === 'error-no-client'){
                        self.pos_widget.screen_selector.show_popup('error',{
                            message: _t('An anonymous order cannot be invoiced'),
                            comment: _t('Please select a client for this order. This can be done by clicking the order tab'),
                        });
                    }else{
                        self.pos_widget.screen_selector.show_popup('error',{
                            message: _t('The order could not be sent'),
                            comment: _t('Check your internet connection and try again.'),
                        });
                    }
                    self.pos_widget.action_bar.set_button_disabled('validation',false);
                    self.pos_widget.action_bar.set_button_disabled('invoice',false);
                });

                invoiced.done(function(){
                    self.pos_widget.action_bar.set_button_disabled('validation',false);
                    self.pos_widget.action_bar.set_button_disabled('invoice',false);
                    self.pos.get('selectedOrder').destroy();
                });

            }else{
                self.pos.push_order(currentOrder) 
                if(self.pos.config.iface_print_via_proxy){
                    var receipt = currentOrder.export_for_printing();
                    self.pos.proxy.print_receipt(QWeb.render('XmlReceipt',{
                        receipt: receipt, widget: self,
                    }));
                    self.pos.get('selectedOrder').destroy();    //finish order and go back to scan screen
                }else{
                    self.pos_widget.screen_selector.set_current_screen(self.next_screen);
                }
            }
                
            // Orinal
            setTimeout(function(){
                    document.activeElement.blur();
                    $("input").blur();
                },100);



        },
        validate_order: function(options) {
            var self = this;

            openerp_pos_models(instance,module);
            options = options || {};

            var currentOrder = this.pos.get('selectedOrder');

            try {

                var product_product_list = []
                var product_product_dict = new Object();

                for (var count = 0; count < currentOrder.get('orderLines').models.length ; count++)
                {   
                    product_id = currentOrder.get('orderLines').models[count]['product']['id'];
                    product_qty = currentOrder.get('orderLines').models[count]['quantity'];
                    product_product_list.push(product_id);
                    product_product_dict[product_id] = product_qty;
                    if (product_qty <= 0)
                    {
                        self.pos_widget.screen_selector.show_popup('error',{
                                'message': _t('Error'),
                                'comment': _t('Can not add products with quantity <= 0'),
                        });
                        return ;
                    }

                }
                
                var product_product_model = new openerp.web.Model('product.product');

                product_product_model.call('search_read', [[['id', 'in', product_product_list]],['name','qty_available']]).done(function(values){
                    // title_message = 'List of products are not enough quantity to sale';
                    content_message = '';
                    var check_flag = 0;
                    
                    for (var j = 0 ; j < values.length ; j++)
                    {
                        p_id = values[j]['id'];
                        p_name = values[j]['name'];
                        p_quantity = values[j]['qty_available'];
                        // console.log(p_quantity);
                        if (p_quantity < product_product_dict[p_id])
                        {
                            check_flag = 1;
                            content_message = content_message + p_name +' : ' + p_quantity.toString() + ';\n\n';
                            
                        }
                    }

                    if (check_flag == 1)
                    {
                        self.pos_widget.screen_selector.show_popup('error',{
                                'message': _t('List of products are not enough quantity to sale'),
                                'comment': _t(content_message),
                        });
                        return ;
                    }
                    
                    self.after_validate_order(options, currentOrder);
                    // hide onscreen (iOS) keyboard 
         
                }).fail(function (err, ev) {
                    self.after_validate_order(options, currentOrder);
                        // Prevent the CrashManager to display an error
                        // in case of an xhr error not due to a server error
                    ev.preventDefault();
                });
            } catch(e) {
                console.error(e);
                return;
        }

        },
    });
};