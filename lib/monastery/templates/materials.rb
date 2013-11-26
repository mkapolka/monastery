require 'monastery/templates/template.rb'

module Templates
    class Template
        class << self
            alias_method :material, :mixin
        end
    end

    class Material < UniqueSubtemplate
        self.container_property = Properties::Material
    end

    class Metal < Material
        #self.properties += [Hard, Conductive]
        self.properties = [Hard, Waterproof]
    end

    class Paper < Material
        self.properties = []
    end

    class Porcelain < Material
        self.properties = [Hard, Brittle]
    end
end
