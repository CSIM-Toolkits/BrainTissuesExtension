#include "itkImageFileWriter.h"
#include "itkImage.h"

#include "itkPluginUtilities.h"
#include "itkThresholdImageFilter.h"
#include "itkStatisticsImageFilter.h"
#include "itkDivideImageFilter.h"
#include "itkScalarImageKmeansImageFilter.h"

#include "BasicBrainTissuesCLP.h"

// Use an anonymous namespace to keep class types and function names
// from colliding when module is used as shared object module.  Every
// thing should be in an anonymous namespace except for the module
// entry point, e.g. main()
//
namespace
{

template <class T>
int DoIt( int argc, char * argv[], T )
{
    PARSE_ARGS;

    typedef    float                    InputPixelType;
    typedef    unsigned char            OutputPixelType;
    const unsigned int                  Dimension=3;
    const unsigned int                  numClass=4;

    typedef itk::Image<InputPixelType,  Dimension> InputImageType;
    typedef itk::Image<OutputPixelType, Dimension> OutputImageType;

    typedef itk::ImageFileReader<InputImageType>    ReaderType;

    typename ReaderType::Pointer reader = ReaderType::New();
    reader->SetFileName( inputVolume.c_str() );
    reader->Update();

    typedef itk::StatisticsImageFilter<InputImageType> StatisticType;
    typename StatisticType::Pointer stat = StatisticType::New();
    stat->SetInput(reader->GetOutput());
    stat->Update();
    double meanValues[numClass];

    double guessByContrast = (stat->GetMaximum() - stat->GetMinimum())/numClass;
    for (int n = 0; n < numClass; ++n) {
        meanValues[n]=guessByContrast*(n+1);
    }

    //Apply segmentation procedure
    //K-Means Segmentation Approach
    typedef itk::ScalarImageKmeansImageFilter< InputImageType > KMeansFilterType;
    KMeansFilterType::Pointer kmeansFilter = KMeansFilterType::New();
    kmeansFilter->SetInput( reader->GetOutput() );
    const unsigned int numberOfInitialClasses = numClass;

    for( unsigned k=0; k < numberOfInitialClasses; k++ )
    {
        kmeansFilter->AddClassWithInitialMean(meanValues[k]);
    }

    kmeansFilter->Update();

    if (imageModality=="T1") {
        if (oneTissue) {
            KMeansFilterType::OutputImagePixelType tissueValue;
            if (typeTissue == "White Matter") {
                tissueValue = 3;
            }else if (typeTissue == "Gray Matter") {
                tissueValue = 2;
            }else if (typeTissue == "CSF") {
                tissueValue = 1;
            }

            //Take only the tissue of interest
            typedef itk::ThresholdImageFilter <OutputImageType>     ThresholdImageFilterType;
            typename  ThresholdImageFilterType::Pointer thresholdFilter  = ThresholdImageFilterType::New();
            thresholdFilter->SetInput(kmeansFilter->GetOutput());
            thresholdFilter->ThresholdOutside(tissueValue, tissueValue);
            thresholdFilter->SetOutsideValue(0);

            //Changing mask value to 1
            typedef itk::DivideImageFilter<OutputImageType, OutputImageType, OutputImageType>   DivideType;
            typename DivideType::Pointer divide = DivideType::New();
            divide->SetInput1(thresholdFilter->GetOutput());
            divide->SetConstant2(tissueValue);
            divide->Update();

            KMeansFilterType::ParametersType estimatedMeans =
                    kmeansFilter->GetFinalMeans();
            const unsigned int numberOfClasses = estimatedMeans.Size();
            for ( unsigned int i = 0; i < numberOfClasses; ++i )
            {
                std::cout << "cluster[" << i << "] ";
                std::cout << "    estimated mean : " << estimatedMeans[i] << std::endl;
            }

            typedef itk::ImageFileWriter<OutputImageType> WriterType;
            typename WriterType::Pointer writer = WriterType::New();
            writer->SetFileName( outputLabel.c_str() );
            writer->SetInput( divide->GetOutput() );
            writer->SetUseCompression(1);
            writer->Update();
            return EXIT_SUCCESS;
        }else{
            //        Take all the segmented tissues
            KMeansFilterType::ParametersType estimatedMeans =
                    kmeansFilter->GetFinalMeans();
            const unsigned int numberOfClasses = estimatedMeans.Size();
            for ( unsigned int i = 0; i < numberOfClasses; ++i )
            {
                std::cout << "cluster[" << i << "] ";
                std::cout << "    estimated mean : " << estimatedMeans[i] << std::endl;
            }

            typedef KMeansFilterType::OutputImageType  OutputImageType;
            typedef itk::ImageFileWriter< OutputImageType > WriterType;
            WriterType::Pointer writer = WriterType::New();
            writer->SetInput( kmeansFilter->GetOutput() );
            writer->SetUseCompression(1);
            writer->SetFileName( outputLabel.c_str() );
            writer->Update();
            return EXIT_SUCCESS;
        }
    }else if (imageModality=="T2") {
        if (oneTissue) {
            KMeansFilterType::OutputImagePixelType tissueValue;
            if (typeTissue == "White Matter") {
                tissueValue = 1;
            }else if (typeTissue == "Gray Matter") {
                tissueValue = 2;
            }else if (typeTissue == "CSF") {
                tissueValue = 3;
            }

            //Take only the tissue of interest
            typedef itk::ThresholdImageFilter <OutputImageType>     ThresholdImageFilterType;
            typename  ThresholdImageFilterType::Pointer thresholdFilter  = ThresholdImageFilterType::New();
            thresholdFilter->SetInput(kmeansFilter->GetOutput());
            thresholdFilter->ThresholdOutside(tissueValue, tissueValue);
            thresholdFilter->SetOutsideValue(0);

            //Changing mask value to 1
            typedef itk::DivideImageFilter<OutputImageType, OutputImageType, OutputImageType>   DivideType;
            typename DivideType::Pointer divide = DivideType::New();
            divide->SetInput1(thresholdFilter->GetOutput());
            divide->SetConstant2(tissueValue);
            divide->Update();

            KMeansFilterType::ParametersType estimatedMeans =
                    kmeansFilter->GetFinalMeans();
            const unsigned int numberOfClasses = estimatedMeans.Size();
            for ( unsigned int i = 0; i < numberOfClasses; ++i )
            {
                std::cout << "cluster[" << i << "] ";
                std::cout << "    estimated mean : " << estimatedMeans[i] << std::endl;
            }

            typedef itk::ImageFileWriter<OutputImageType> WriterType;
            typename WriterType::Pointer writer = WriterType::New();
            writer->SetFileName( outputLabel.c_str() );
            writer->SetInput( divide->GetOutput() );
            writer->SetUseCompression(1);
            writer->Update();
            return EXIT_SUCCESS;
        }else{
            //        Take all the segmented tissues
            KMeansFilterType::ParametersType estimatedMeans =
                    kmeansFilter->GetFinalMeans();
            const unsigned int numberOfClasses = estimatedMeans.Size();
            for ( unsigned int i = 0; i < numberOfClasses; ++i )
            {
                std::cout << "cluster[" << i << "] ";
                std::cout << "    estimated mean : " << estimatedMeans[i] << std::endl;
            }

            typedef KMeansFilterType::OutputImageType  OutputImageType;
            typedef itk::ImageFileWriter< OutputImageType > WriterType;
            WriterType::Pointer writer = WriterType::New();
            writer->SetInput( kmeansFilter->GetOutput() );
            writer->SetUseCompression(1);
            writer->SetFileName( outputLabel.c_str() );
            writer->Update();
            return EXIT_SUCCESS;
        }
    }else if (imageModality=="PD") {
        if (oneTissue) {
            KMeansFilterType::OutputImagePixelType tissueValue;
            if (typeTissue == "White Matter") {
                tissueValue = 1;
            }else if (typeTissue == "Gray Matter") {
                tissueValue = 2;
            }else if (typeTissue == "CSF") {
                tissueValue = 3;
            }

            //Take only the tissue of interest
            typedef itk::ThresholdImageFilter <OutputImageType>     ThresholdImageFilterType;
            typename  ThresholdImageFilterType::Pointer thresholdFilter  = ThresholdImageFilterType::New();
            thresholdFilter->SetInput(kmeansFilter->GetOutput());
            thresholdFilter->ThresholdOutside(tissueValue, tissueValue);
            thresholdFilter->SetOutsideValue(0);

            //Changing mask value to 1
            typedef itk::DivideImageFilter<OutputImageType, OutputImageType, OutputImageType>   DivideType;
            typename DivideType::Pointer divide = DivideType::New();
            divide->SetInput1(thresholdFilter->GetOutput());
            divide->SetConstant2(tissueValue);
            divide->Update();

            KMeansFilterType::ParametersType estimatedMeans =
                    kmeansFilter->GetFinalMeans();
            const unsigned int numberOfClasses = estimatedMeans.Size();
            for ( unsigned int i = 0; i < numberOfClasses; ++i )
            {
                std::cout << "cluster[" << i << "] ";
                std::cout << "    estimated mean : " << estimatedMeans[i] << std::endl;
            }

            typedef itk::ImageFileWriter<OutputImageType> WriterType;
            typename WriterType::Pointer writer = WriterType::New();
            writer->SetFileName( outputLabel.c_str() );
            writer->SetInput( divide->GetOutput() );
            writer->SetUseCompression(1);
            writer->Update();
            return EXIT_SUCCESS;
        }else{
            //        Take all the segmented tissues
            KMeansFilterType::ParametersType estimatedMeans =
                    kmeansFilter->GetFinalMeans();
            const unsigned int numberOfClasses = estimatedMeans.Size();
            for ( unsigned int i = 0; i < numberOfClasses; ++i )
            {
                std::cout << "cluster[" << i << "] ";
                std::cout << "    estimated mean : " << estimatedMeans[i] << std::endl;
            }

            typedef KMeansFilterType::OutputImageType  OutputImageType;
            typedef itk::ImageFileWriter< OutputImageType > WriterType;
            WriterType::Pointer writer = WriterType::New();
            writer->SetInput( kmeansFilter->GetOutput() );
            writer->SetUseCompression(1);
            writer->SetFileName( outputLabel.c_str() );
            writer->Update();
            return EXIT_SUCCESS;
        }
    }

    return EXIT_SUCCESS;
}

} // end of anonymous namespace

int main( int argc, char * argv[] )
{
    PARSE_ARGS;

    itk::ImageIOBase::IOPixelType     pixelType;
    itk::ImageIOBase::IOComponentType componentType;

    try
    {
        itk::GetImageType(inputVolume, pixelType, componentType);

        // This filter handles all types on input, but only produces
        // signed types
        switch( componentType )
        {
        case itk::ImageIOBase::UCHAR:
            return DoIt( argc, argv, static_cast<unsigned char>(0) );
            break;
        case itk::ImageIOBase::CHAR:
            return DoIt( argc, argv, static_cast<char>(0) );
            break;
        case itk::ImageIOBase::USHORT:
            return DoIt( argc, argv, static_cast<unsigned short>(0) );
            break;
        case itk::ImageIOBase::SHORT:
            return DoIt( argc, argv, static_cast<short>(0) );
            break;
        case itk::ImageIOBase::UINT:
            return DoIt( argc, argv, static_cast<unsigned int>(0) );
            break;
        case itk::ImageIOBase::INT:
            return DoIt( argc, argv, static_cast<int>(0) );
            break;
        case itk::ImageIOBase::ULONG:
            return DoIt( argc, argv, static_cast<unsigned long>(0) );
            break;
        case itk::ImageIOBase::LONG:
            return DoIt( argc, argv, static_cast<long>(0) );
            break;
        case itk::ImageIOBase::FLOAT:
            return DoIt( argc, argv, static_cast<float>(0) );
            break;
        case itk::ImageIOBase::DOUBLE:
            return DoIt( argc, argv, static_cast<double>(0) );
            break;
        case itk::ImageIOBase::UNKNOWNCOMPONENTTYPE:
        default:
            std::cout << "unknown component type" << std::endl;
            break;
        }
    }

    catch( itk::ExceptionObject & excep )
    {
        std::cerr << argv[0] << ": exception caught !" << std::endl;
        std::cerr << excep << std::endl;
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
