class Thing
    attr_accessor :properties, :name, :description

    def initialize
        @properties = {}
        @name = "a thing"
        @description = ""
    end

    def destroy
        self.properties.values.each do |property|
            property.owner = nil
            property.unmake
        end
        self.properties.clear
    end

    def method_missing(method_name, *args, &block)
        #Nice way of getting at properties
        return @properties[method_name] if @properties.has_key? method_name
        return @properties[method_name.capitalize] if @properties.has_key? method_name.capitalize
        super
    end

    def properties(types=nil)
        return @properties if types == nil
        return @properties.select{|key, property| property.types.include? types}
    end

    def get_property(property_class)
        return @properties[property_class.key]
    end

    def set_property(property_class, property_object)
        property_object.owner = self
        @properties[property_class.key] = property_object
    end

    def delete_property(property_class)
        property_object.owner = nil
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

        property.make()
    end

    def call(method_name, args=nil)
        self.properties.each do |key, property|
            property.send(method_name, *args) if property.class.method_defined? method_name
        end
        clear_unmade_properties
    end

    def unmake(property_class)
        property_key = property_class.key
        if self.has_property? property_class
            self.get_property(property_class).count -= 1
        end
    end

    def clear_unmade_properties
        self.properties.reject!{|key, value| value.count <= 0}
    end

    def is?(property_class)
        has_property?(property_class) && self.get_property(property_class).count > 0
    end

    def not?(property_class)
        not is? property_class
    end

    def describe(method)
        description = ""
        properties.values.each do |property|
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
