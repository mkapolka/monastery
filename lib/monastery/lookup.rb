require 'active_support/core_ext/class/attribute'

def finds_constants_in(*places)
    self.class_eval do
        class_attribute :const_search_locations
        self.const_search_locations = places

        def self.const_missing(constant_name)
            self.const_search_locations.each do |place|
                return place.const_get(constant_name) if place.const_defined? constant_name
            end
            raise NameError.new("Couldn't find constant #{constant_name} even after searching extra locations")
        end
    end
end
