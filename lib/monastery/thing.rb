module Things
    class Thing
        attr_accessor :properties, :name, :description

        def initialize
            @properties = {}
            @name = "a thing"
            @description = ""
        end

        def method_missing(method_name, *args, &block)
            #Nice way of getting at properties
            return @properties[method_name] if @properties.has_key? method_name
            return @properties[method_name.capitalize] if @properties.has_key? method_name.capitalize
            super
        end

        def properties(types=nil)
            return @properties if types == nil
            return @properties.select{|property| property.types.include? types}
        end

        def get_property(property_class)
            return @properties[property_class.key]
        end

        def set_property(property_class, property_object)
            @properties[property_class.key] = property_object
        end

        def delete_property(property_class)
            @properties.delete property_class.key
        end

        def has_property?(property_class)
            @properties.include? property_class.key
        end

        def make(property_class)
            if self.has_property? property_class
                property = get_property(property_class)
                property.count += 1
            else
                property = property_class.new
                property.count = 1
                set_property(property_class, property)
            end

            property.make(self)
        end

        def call(method_name, args)
            self.properties.each do |key, property|
                property.send(method_name, args) if property.class.method_defined? method_name
            end
        end

        def unmake(property_class)
            property_key = property_class.key
            if self.has_property? property_class
                if self.get_property(property_class).count > 1
                    self.get_property(property_class).count -= 1
                else
                    properties.delete(property_key)
                end
            end
        end

        def is?(property_class)
            self.has_property?(property_class) && self.get_property(property_class).count > 0
        end

        def describe(method)
            description = ""
            properties.each do |property|
                if property.revealed_by? method
                    description += property.describe
                end
            end
            return description
        end

        def say(message)
            puts message
        end
        
        def materials=(material_class)
            material_class.apply(self)
        end
    end
end
