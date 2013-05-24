################################################################################
#                                                                              #
# Metaproperties                                                               #
#                                                                              #
################################################################################

module Properties
   class Property_Lender < Property
      attr_accessor :lends_types
      def initialize
         @lends_types = [];
      end

      upon :added_to do |me, container|
         puts "Lending #{lends_types}"
         container.make *me.properties_of_type(self.lends_types);
         me.unmake *me.properties_of_type(self.lends_types);
      end
      
      upon :removed_from do |me, container|
         container.unmake *me.properties_of_type(self.lends_types);
         me.make *me.properties_of_type(self.lends_types);
      end
   end
end

class Noun
   def lends_properties(*args)
      is :property_lender
      self.property_lender.lends_types = args;
   end
end
